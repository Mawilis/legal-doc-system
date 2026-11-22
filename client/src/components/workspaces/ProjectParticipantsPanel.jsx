/**
 * TITLE: WILSY OS Governed Project Participants Workspace
 * VERSION: v1.6.0-SEPARATE-SOURCE-FAILURE-CLASSIFICATION
 * AUTHORITY: Python EOS Projects IAM, principal and membership truth only.
 * EPITOME: Select eligible exact-tenant members; grant and revoke explicit
 *          project VIEWER/CONTRIBUTOR participation with audited source readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectParticipantsPanel.jsx
 * COLLABORATION / OWNERSHIP: ProjectsWorkspace mounts exact-project owner UI;
 *          api.js supplies existing authenticated session transport.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.6.0-SEPARATE-SOURCE-FAILURE-CLASSIFICATION identifies failing participant-list versus eligible-member directory read, including HTTP denial/unavailability and invalid source schema. No roster is guessed and grant remains fail-closed until both exact-scope reads validate.
 * CHANGELOG: v1.5.0-ELIGIBILITY-EMPTY-STATE-EXPLANATION explains the absence of eligible tenant members in the contributor selector and distinguishes membership/IAM admissions from project participation; preserves EOS-only grants and existing errors.
 * CHANGELOG: v1.4.0-ASSIGNEE-EDITOR-READBACK-HANDOFF notifies a mounting work editor only after a participant grant/revoke has been independently source-read back. Does not grant IAM or task authority.
 * CHANGELOG: v1.3.0-NO-BACKEND-IDENTITY-PRESENTATION removes long principal codes from the
 *          visible member-choice surface while preserving the exact source
 *          identity as an EOS-only command input and audit key.
 * CHANGELOG: v1.2.0-HUMAN-IDENTITY-AUDIT-SEPARATION removes raw
 *          principal IDs and record revisions from operating People cards;
 *          identifiers remain stored and used exclusively for EOS commands.
 * CHANGELOG: v1.1.0-SOURCE-NAMED-PARTICIPANTS presents exact-tenant
 *          source-supplied first/last names ahead of opaque principal IDs,
 *          validates optional name fields and improves form contrast and
 *          keyboard accessibility without changing IAM or submission IDs.
 * CHANGELOG: v1.0.0-EXACT-TENANT-PROJECT-PARTICIPATION adds a choice-based,
 *          source-backed participant lifecycle, not an IAM/admission shortcut.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Names only from EOS scoped projections; no fake names,
 *          employee details, raw tokens or inferred project permissions.
 * TENANT BOUNDARY: Each response validates exact tenant, principal and project.
 * AUTHORITY BOUNDARY: Project participation is never a substitute for current
 *          membership, explicit role possession and active entitlement.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { LoaderCircle, RefreshCw, ShieldCheck, UserPlus, UserMinus } from 'lucide-react';
import api from '../../services/api.js';

const PARTICIPANTS = 'WILSY-PROJECT-PARTICIPANT-LIST/V1';
const OPTIONS = 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1';
const RESULT = 'WILSY-PROJECT-PARTICIPANT-RESULT/V1';

function validParticipants(data, { tenantId, principalId, projectId }, offset) {
  if (
    data?.schema !== PARTICIPANTS || data.tenant_id !== tenantId
    || data.principal_id !== principalId || data.project_id !== projectId
    || data.limit !== 50 || data.offset !== offset
    || !Array.isArray(data.items) || data.items.length > 50
    || typeof data.has_more !== 'boolean'
    || data.next_offset !== (data.has_more ? offset + data.items.length : null)
    || data.items.some(item => (
      item.tenant_id !== tenantId || item.project_id !== projectId
      || item.state !== 'ACTIVE'
      || !['VIEWER', 'CONTRIBUTOR'].includes(item.role)
      || typeof item.principal_id !== 'string'
      || !Number.isSafeInteger(item.revision) || item.revision < 1
      || !/^[a-f0-9]{128}$/.test(item.fingerprint || '')
    ))
  ) throw new Error('PROJECT_PARTICIPANT_SOURCE_INVALID');
  return data;
}

function validOptions(data, { tenantId, principalId, projectId }, offset) {
  if (
    data?.schema !== OPTIONS || data.tenant_id !== tenantId
    || data.principal_id !== principalId || data.project_id !== projectId
    || data.limit !== 50 || data.offset !== offset
    || !Array.isArray(data.items) || data.items.length > 50
    || typeof data.has_more !== 'boolean'
    || data.next_offset !== (data.has_more ? offset + 50 : null)
    || data.items.some(item => typeof item.principal_id !== 'string' || !item.principal_id
      || !['first_name', 'last_name'].every(field => item[field] === undefined
        || item[field] === null || (typeof item[field] === 'string'
          && item[field].trim() === item[field] && item[field].length > 0
          && item[field].length <= 100)))
  ) throw new Error('PROJECT_PARTICIPANT_CHOICES_INVALID');
  return data;
}

/** Display-only source names; identity and commands continue using principal_id. */
function optionName(person) {
  const parts = [person.first_name, person.last_name].filter(value =>
    typeof value === 'string' && value.trim());
  return parts.length ? parts.join(' ') : null;
}

/** @description A source-owned project participant management surface. */
export default function ProjectParticipantsPanel({ projectId, tenantId, principalId, tenantHeaders, onParticipantsChanged = null }) {
  const [items, setItems] = useState([]);
  const [choices, setChoices] = useState([]);
  const [offset, setOffset] = useState(0);
  const [optionOffset, setOptionOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [hasMoreChoices, setHasMoreChoices] = useState(false);
  const [state, setState] = useState('LOADING');
  const [error, setError] = useState('');
  const [selectedPrincipal, setSelectedPrincipal] = useState('');
  const [selectedRole, setSelectedRole] = useState('CONTRIBUTOR');
  const [busy, setBusy] = useState(false);
  const generation = useRef(0);
  const replay = useRef({ fingerprint: '', key: '' });
  const scope = [tenantId, principalId, projectId].join('\0');
  const currentScope = useRef(scope);
  currentScope.current = scope;
  const root = '/projects/' + encodeURIComponent(projectId);
  const headers = tenantHeaders || {};
  const coordinates = { tenantId, principalId, projectId };

  const load = useCallback(async (personOffset = 0, membersOffset = 0) => {
    const current = ++generation.current;
    const active = scope;
    setState(previous => previous === 'READY' ? 'REFRESHING' : 'LOADING');
    setError('');
    try {
      const [peopleResult, optionsResult] = await Promise.allSettled([
        api.get(root + '/participants?limit=50&offset=' + personOffset, { headers }),
        api.get(root + '/participant-options?limit=50&offset=' + membersOffset, { headers }),
      ]);
      if (current !== generation.current || currentScope.current !== active) return false;
      const sourceError = (result, name) => {
        if (result.status === 'fulfilled') return null;
        const status = result.reason?.response?.status;
        const category = status === 401 ? 'authentication required'
          : status === 403 ? 'permission denied'
            : status === 404 ? 'endpoint not available in this EOS runtime'
              : status === 503 ? 'EOS source unavailable'
                : status === 422 ? 'source request rejected'
                  : Number.isInteger(status) ? 'HTTP ' + status : 'network unavailable';
        const error = new Error(name + ': ' + category + '.');
        error.response = result.reason?.response;
        error.sourceMessage = name + ': ' + category + '.';
        return error;
      };
      const readFailure = sourceError(peopleResult, 'Project participants')
        || sourceError(optionsResult, 'Eligible tenant member directory');
      if (readFailure) throw readFailure;
      let verified;
      let permitted;
      try {
        verified = validParticipants(peopleResult.value.data, coordinates, personOffset);
      } catch {
        const error = new Error('PROJECT_PARTICIPANT_LIST_INVALID');
        error.sourceMessage = 'Project participants: response scope or schema could not be verified.';
        throw error;
      }
      try {
        permitted = validOptions(optionsResult.value.data, coordinates, membersOffset);
      } catch {
        const error = new Error('PROJECT_MEMBER_CHOICES_INVALID');
        error.sourceMessage = 'Eligible tenant member directory: response scope or schema could not be verified.';
        throw error;
      }
      setItems(verified.items);
      setChoices(permitted.items);
      setHasMore(verified.has_more);
      setHasMoreChoices(permitted.has_more);
      setOffset(personOffset);
      setOptionOffset(membersOffset);
      setState('READY');
      return true;
    } catch (cause) {
      if (current !== generation.current || currentScope.current !== active) return false;
      setItems([]);
      setChoices([]);
      const code = cause?.response?.status;
      setError(cause?.sourceMessage
        ? cause.sourceMessage + ' Refresh after the underlying EOS source is available.'
        : code === 401 ? 'Authentication required for project participants.'
          : code === 403 ? 'EOS denied participant management.'
            : 'Project participant sources could not be verified. Retry.');
      setState(code === 401 || code === 403 ? 'DENIED' : 'UNAVAILABLE');
      return false;
    }
  }, [scope, root, tenantHeaders, tenantId, principalId, projectId]);

  useEffect(() => {
    generation.current += 1;
    setItems([]);
    setChoices([]);
    setSelectedPrincipal('');
    setSelectedRole('CONTRIBUTOR');
    replay.current = { fingerprint: '', key: '' };
    void load(0, 0);
    return () => { generation.current += 1; };
  }, [scope, load]);

  const retainKey = fingerprint => {
    if (!replay.current.key || replay.current.fingerprint !== fingerprint) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        throw new Error('PROJECT_PARTICIPANT_IDEMPOTENCY_UNAVAILABLE');
      }
      replay.current = { fingerprint, key: globalThis.crypto.randomUUID() };
    }
    return replay.current.key;
  };

  const execute = async (fingerprint, action) => {
    if (busy || state !== 'READY') return;
    const active = scope;
    setBusy(true);
    setError('');
    try {
      const key = retainKey(fingerprint);
      const { data } = await action(key);
      if (currentScope.current !== active) return;
      if (
        data?.schema !== RESULT || data.tenant_id !== tenantId
        || data.principal_id !== principalId || data.project_id !== projectId
        || !data.participant || data.participant.tenant_id !== tenantId
        || data.participant.project_id !== projectId
        || !['ACTIVE', 'REVOKED'].includes(data.participant.state)
      ) throw new Error('PROJECT_PARTICIPANT_RESULT_INVALID');
      const verified = await load(0, 0);
      if (!verified || currentScope.current !== active) return;
      replay.current = { fingerprint: '', key: '' };
      setSelectedPrincipal('');
      if (typeof onParticipantsChanged === 'function') onParticipantsChanged();
    } catch (cause) {
      if (currentScope.current !== active) return;
      const code = cause?.response?.status;
      setError(code === 403 ? 'EOS denied this participant command.'
        : code === 409 ? 'Participant state changed or this principal is not eligible. Refresh and reconcile.'
          : 'EOS could not verify participant command persistence. Refresh before retrying.');
    } finally {
      if (currentScope.current === active) setBusy(false);
    }
  };

  const grant = event => {
    event.preventDefault();
    if (!selectedPrincipal || !choices.some(person => person.principal_id === selectedPrincipal)) return;
    const body = { principal_id: selectedPrincipal, role: selectedRole };
    void execute(JSON.stringify(['grant', body]), key =>
      api.post(root + '/participants', body, {
        headers: { ...headers, 'Idempotency-Key': key },
      }),
    );
  };

  const revoke = item => {
    void execute(JSON.stringify(['revoke', item.principal_id, item.revision]), key =>
      api.post(root + '/participants/' + encodeURIComponent(item.principal_id) + '/revoke',
        { expected_revision: item.revision },
        { headers: { ...headers, 'Idempotency-Key': key } }),
    );
  };

  return <section className="wp-project-participants mt-5 border-t border-slate-200 pt-4" aria-label="Project participants">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h3 className="text-base font-semibold text-slate-900">Project participants</h3>
        <p className="mt-1 text-xs text-slate-600">
          Governed, project-specific viewer and contributor assignments. EOS also requires separately assigned IAM.
        </p>
      </div>
      <button type="button" onClick={() => void load(offset, optionOffset)}
        disabled={busy} className="wp-button"><RefreshCw size={14}/> Refresh participants</button>
    </div>
    {(state === 'LOADING' || state === 'REFRESHING') &&
      <p role="status" className="mt-3 flex items-center gap-2 text-sm text-slate-600">
        <LoaderCircle size={14} className="animate-spin"/> Verifying participants…
      </p>}
    {(state === 'DENIED' || state === 'UNAVAILABLE') &&
      <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {state === 'READY' && <>
      <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200">
        {items.map(item => <li key={item.principal_id}
          className="flex flex-wrap items-center justify-between gap-2 bg-white p-3">
          <div>
            <div className="flex items-center gap-2 font-semibold text-slate-900">
              <ShieldCheck size={15}/> <span className="break-words">{optionName(choices.find(person => person.principal_id === item.principal_id) || {}) || 'Verified project participant'}</span>
            </div>
            <p className="mt-1 text-xs text-slate-600">
              {item.role === 'CONTRIBUTOR' ? 'Contributor' : 'Viewer'}
            </p>
          </div>
          <button type="button" disabled={busy} onClick={() => revoke(item)}
            className="wp-button wp-button-danger !min-h-8 !px-2 !py-1 !text-xs">
            <UserMinus size={14}/> Revoke participation
          </button>
        </li>)}
        {items.length === 0 && <li className="p-4 text-sm text-slate-600">No verified active participants on this page.</li>}
      </ul>
      {(hasMore || offset > 0) && <nav aria-label="Participant pages"
        className="mt-2 flex items-center justify-between gap-2">
        <button type="button" className="wp-button" disabled={busy || !offset}
          onClick={() => void load(Math.max(0, offset - 50), optionOffset)}>Previous participants</button>
        <span className="text-xs text-slate-600">Page {Math.floor(offset / 50) + 1}</span>
        <button type="button" className="wp-button" disabled={busy || !hasMore}
          onClick={() => void load(offset + 50, optionOffset)}>Next participants</button>
      </nav>}
      <form onSubmit={grant} className="mt-4 grid gap-4 rounded-xl border border-slate-300 bg-white p-4 sm:grid-cols-[minmax(0,1fr)_minmax(180px,.6fr)]">
        <label className="block text-sm font-semibold text-slate-950">Eligible tenant member
          <select aria-label="Eligible participant" required value={selectedPrincipal}
            onChange={event => setSelectedPrincipal(event.target.value)}
            className="mt-2 min-h-12 w-full min-w-0 rounded-lg border border-slate-400 bg-white px-3 py-2.5 text-base font-medium text-slate-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">
            <option value="">Select a verified member by name</option>
            {choices.map(person =>
              <option key={person.principal_id} value={person.principal_id}>{optionName(person) || 'Verified member — name unavailable'}</option>)}
          </select>

        </label>
        {choices.length === 0 && !hasMoreChoices && <p role="status" className="sm:col-span-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-800">
          EOS has not verified any eligible tenant member for project participation. A current tenant membership and matching business IAM role must be established through their independent governed workflows before this project can grant contributor access. No automatic Founder or owner privilege is inferred.
        </p>}
        <label className="block text-sm font-semibold text-slate-950">Project role
          <select aria-label="Project participation role" value={selectedRole}
            onChange={event => setSelectedRole(event.target.value)}
            className="mt-2 min-h-12 w-full min-w-0 rounded-lg border border-slate-400 bg-white px-3 py-2.5 text-base font-medium text-slate-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">
            <option value="CONTRIBUTOR">Contributor</option>
            <option value="VIEWER">Viewer</option>
          </select>
        </label>
        <div className="sm:col-span-2 flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-slate-700">
            Participation never grants IAM. The member must separately hold the matching role to access project work.
          </div>
          <button type="submit" disabled={busy || !selectedPrincipal}
            className="wp-button wp-button-primary"><UserPlus size={14}/> Add participant</button>
        </div>
        {(hasMoreChoices || optionOffset > 0) && <nav aria-label="Eligible member pages"
          className="flex items-center gap-2 sm:col-span-2">
          <button type="button" className="wp-button" disabled={busy || optionOffset === 0}
            onClick={() => void load(offset, Math.max(0, optionOffset - 50))}>Previous members</button>
          <span className="text-xs text-slate-600">Member page {Math.floor(optionOffset / 50) + 1}</span>
          <button type="button" className="wp-button" disabled={busy || !hasMoreChoices}
            onClick={() => void load(offset, optionOffset + 50)}>Next members</button>
        </nav>}
      </form>
    </>}
    {state === 'READY' && error && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
  </section>;
}

// ARTIFACT: ProjectParticipantsPanel.jsx
// VERSION: v1.6.0-SEPARATE-SOURCE-FAILURE-CLASSIFICATION
// AUTHORITY BOUNDARY: non-possessory project grant/revoke only; EOS enforces IAM
// TENANT POSTURE: exact source tenant, principal and project
// FAIL-CLOSED POSTURE: foreign, malformed, stale, denied or uncertain states reject
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
