/**
 * TITLE: WILSY OS Governed Project Notes Workspace
 * VERSION: v1.0.0-EOS-SOURCE-BACKED-PROJECT-NOTES
 * AUTHORITY: Authenticated Python EOS Projects note API exclusively.
 * EPITOME: In-project note list, author-owned create/revise/archive, source
 *          readback and explicit denial/unavailable states, without local truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectNotesPanel.jsx
 * COLLABORATION / OWNERSHIP: ProjectsWorkspace mounts this presentation;
 *          api.js transports exact session and Python EOS owns all commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.0.0-EOS-SOURCE-BACKED-PROJECT-NOTES establishes one governed
 *          collaborative note surface with preserved idempotency across retry.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: React escapes note text; no HTML/Markdown
 *          authority, synthetic approvals, unauthorized mentions or attachments.
 * TENANT BOUNDARY: Every response validates exact tenant, principal, project
 *          and note scope; session changes invalidate late results.
 * AUTHORITY BOUNDARY: Buttons submit requests only; EOS independently enforces
 *          membership, project scope, permission, entitlement and author CAS.
 * FINANCIAL AUTHORITY BOUNDARY: Notes have no financial authority; Kennel EOS only.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { FileText, LoaderCircle, Plus, RefreshCw } from 'lucide-react';
import api from '../../services/api.js';

const IDENTIFIER = /^pnt-[0-9a-f]{48}$/;
const SCHEMA_LIST = 'WILSY-PROJECT-NOTE-LIST/V1';
const SCHEMA_RESULT = 'WILSY-PROJECT-NOTE-RESULT/V1';

function checkNote(note, tenantId, projectId) {
  return note && note.tenant_id === tenantId && note.project_id === projectId
    && IDENTIFIER.test(note.note_id)
    && typeof note.author_principal_id === 'string'
    && typeof note.body === 'string'
    && Number.isSafeInteger(note.revision) && note.revision >= 1
    && typeof note.fingerprint === 'string' && /^[a-f0-9]{128}$/.test(note.fingerprint);
}

/** @description No browser-controlled business authority; source readback only. */
export default function ProjectNotesPanel({
  projectId, tenantId, principalId, tenantHeaders,
}) {
  const [items, setItems] = useState([]);
  const [state, setState] = useState('LOADING');
  const [draft, setDraft] = useState('');
  const [editor, setEditor] = useState(null);
  const [busy, setBusy] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState('');
  const sequence = useRef(0);
  const commandKey = useRef({ fingerprint: '', key: null });
  const scope = [tenantId, principalId, projectId].join('\0');
  const currentScope = useRef(scope);
  currentScope.current = scope;

  const validateList = useCallback((value, expectedOffset) => {
    if (
      value?.schema !== SCHEMA_LIST || value.tenant_id !== tenantId
      || value.principal_id !== principalId || value.project_id !== projectId
      || value.offset !== expectedOffset || value.limit !== 50
      || typeof value.has_more !== 'boolean'
      || !Array.isArray(value.items) || value.items.length > 50
      || (value.has_more
        ? value.next_offset !== expectedOffset + value.items.length
        : value.next_offset != null)
      || value.items.some(item => !checkNote(item, tenantId, projectId))
      || new Set(value.items.map(item => item.note_id)).size !== value.items.length
    ) throw new Error('PROJECT_NOTE_SOURCE_INVALID');
    return value;
  }, [tenantId, principalId, projectId]);

  const readPage = useCallback(async (nextOffset = 0) => {
    const request = ++sequence.current;
    const scoped = scope;
    setState(current => current === 'READY' ? 'REFRESHING' : 'LOADING');
    setError('');
    try {
      const { data } = await api.get(
        '/projects/' + encodeURIComponent(projectId)
          + '/notes?limit=50&offset=' + nextOffset,
        { headers: tenantHeaders },
      );
      if (request !== sequence.current || currentScope.current !== scoped) return false;
      const verified = validateList(data, nextOffset);
      setItems(verified.items);
      setOffset(nextOffset);
      setHasMore(verified.has_more);
      setState('READY');
      return true;
    } catch (cause) {
      if (request !== sequence.current || currentScope.current !== scoped) return false;
      const http = cause?.response?.status;
      setError(http === 401 ? 'Authentication required for project notes.'
        : http === 403 ? 'EOS denied project notes access.'
          : 'Project notes could not be verified. Retry to restore live state.');
      setState(http === 401 || http === 403 ? 'DENIED' : 'UNAVAILABLE');
      setItems([]);
      setHasMore(false);
      return false;
    }
  }, [scope, projectId, tenantHeaders, validateList]);

  useEffect(() => {
    sequence.current += 1;
    setItems([]);
    setOffset(0);
    setHasMore(false);
    setDraft('');
    setEditor(null);
    setError('');
    commandKey.current = { fingerprint: '', key: null };
    void readPage(0);
    return () => { sequence.current += 1; };
  }, [scope, readPage]);

  const retainedKey = (command) => {
    if (commandKey.current.fingerprint !== command || !commandKey.current.key) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        throw new Error('PROJECT_NOTE_IDEMPOTENCY_UNAVAILABLE');
      }
      commandKey.current = { fingerprint: command, key: globalThis.crypto.randomUUID() };
    }
    return commandKey.current.key;
  };

  const verifyCommand = async (command, action) => {
    if (busy || state !== 'READY') return;
    const originalScope = scope;
    setBusy(true);
    setError('');
    try {
      const key = retainedKey(command);
      const data = await action(key);
      if (currentScope.current !== originalScope) return;
      const result = data?.data;
      if (
        result?.schema !== SCHEMA_RESULT
        || result.tenant_id !== tenantId || result.principal_id !== principalId
        || result.project_id !== projectId
        || !checkNote(result.note, tenantId, projectId)
        || !Array.isArray(result.events)
      ) throw new Error('PROJECT_NOTE_RESULT_INVALID');
      const fresh = await readPage(0);
      if (!fresh || currentScope.current !== originalScope) return;
      commandKey.current = { fingerprint: '', key: null };
      setDraft('');
      setEditor(null);
    } catch (cause) {
      if (currentScope.current !== originalScope) return;
      const code = cause?.response?.status;
      setError(code === 403 ? 'EOS denied this note command.'
        : code === 409 ? 'Note changed or author scope is not current. Refresh before retrying.'
          : 'EOS did not verify the note command. Reconcile before retrying.');
    } finally {
      if (currentScope.current === originalScope) setBusy(false);
    }
  };

  const add = (event) => {
    event.preventDefault();
    const body = draft.trim();
    if (!body || body.length > 10000) return;
    void verifyCommand(JSON.stringify(['create', body]), key =>
      api.post('/projects/' + encodeURIComponent(projectId) + '/notes',
        { body }, { headers: { ...tenantHeaders, 'Idempotency-Key': key } }),
    );
  };

  const revise = (event) => {
    event.preventDefault();
    if (!editor || !editor.body.trim()) return;
    const { note_id, revision } = editor;
    const body = editor.body.trim();
    void verifyCommand(JSON.stringify(['revise', note_id, revision, body]), key =>
      api.patch('/projects/' + encodeURIComponent(projectId) + '/notes/' + encodeURIComponent(note_id),
        { expected_revision: revision, body },
        { headers: { ...tenantHeaders, 'Idempotency-Key': key } }),
    );
  };

  const archive = (note) => {
    if (!note || busy) return;
    void verifyCommand(JSON.stringify(['archive', note.note_id, note.revision]), key =>
      api.post('/projects/' + encodeURIComponent(projectId) + '/notes/'
        + encodeURIComponent(note.note_id) + '/archive',
        { expected_revision: note.revision },
        { headers: { ...tenantHeaders, 'Idempotency-Key': key } }),
    );
  };

  return <section className="wp-project-notes border-t border-slate-200 pt-4" aria-label="Project notes">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <div><h3 className="text-base font-semibold text-slate-900">Project notes</h3>
        <p className="mt-1 text-xs text-slate-600">Source-backed discussion notes. Not approvals or decisions.</p></div>
      <button type="button" onClick={() => void readPage(offset)}
        disabled={busy || state === 'LOADING'}
        className="wp-button inline-flex items-center gap-2"><RefreshCw size={14}/> Refresh</button>
    </div>
    {(state === 'LOADING' || state === 'REFRESHING') &&
      <p role="status" className="mt-2 flex items-center gap-2 text-sm text-slate-600"><LoaderCircle size={15} className="animate-spin"/> Verifying notes…</p>}
    {state === 'DENIED' && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {state === 'UNAVAILABLE' && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {state === 'READY' && <>
      {items.length === 0 && <p className="mt-3 text-sm text-slate-600">No verified notes on this page.</p>}
      <ul className="wp-notes-list mt-3 space-y-3">
        {items.map(item => <li key={item.note_id} className="rounded-xl border border-slate-200 bg-white/90 p-3">
          <div className="flex items-center gap-2"><FileText size={15} className="text-blue-700"/>
            <span className="min-w-0 break-all text-xs text-slate-600">{item.author_principal_id}</span>
            <span className="ml-auto text-xs text-slate-500">Revision {item.revision}</span>
          </div>
          <p className="mt-2 whitespace-pre-wrap break-words text-sm text-slate-900">{item.body}</p>
          {item.author_principal_id === principalId && <div className="mt-3 flex flex-wrap gap-2">
            <button type="button" disabled={busy} className="wp-button"
              onClick={() => setEditor({ note_id: item.note_id, revision: item.revision, body: item.body })}>Edit note</button>
            <button type="button" disabled={busy} className="wp-button wp-button-danger"
              onClick={() => archive(item)}>Archive note</button>
          </div>}
        </li>)}
      </ul>
      {editor && <form onSubmit={revise} className="mt-3 rounded-xl border border-slate-200 p-3">
        <label className="block text-sm font-semibold text-slate-800">Edit your note
          <textarea aria-label="Edit note text" value={editor.body} maxLength={10000} rows={4}
            onChange={event => setEditor(value => ({ ...value, body: event.target.value }))}
            className="mt-2 w-full rounded-lg border border-slate-300 p-3 text-sm font-normal text-slate-900"/>
        </label>
        <div className="mt-2 flex gap-2">
          <button className="wp-button wp-button-primary" type="submit" disabled={busy || !editor.body.trim()}>Save note revision</button>
          <button className="wp-button" type="button" disabled={busy} onClick={() => setEditor(null)}>Cancel</button>
        </div>
      </form>}
      <form onSubmit={add} className="mt-4 border-t border-slate-200 pt-3">
        <label className="block text-sm font-semibold text-slate-800">Add a note
          <textarea value={draft} onChange={event => setDraft(event.target.value)}
            aria-label="New project note" rows={3} maxLength={10000}
            placeholder="Record context, observations, and project discussion…"
            className="mt-2 w-full rounded-lg border border-slate-300 p-3 text-sm font-normal text-slate-900"/>
        </label>
        <button type="submit" disabled={busy || !draft.trim()} className="wp-button wp-button-primary mt-2">
          <Plus size={15}/> Add note to EOS
        </button>
      </form>
      {(hasMore || offset > 0) && <nav aria-label="Project note pages" className="mt-3 flex items-center justify-between gap-2">
        <button type="button" className="wp-button" disabled={busy || offset === 0}
          onClick={() => void readPage(Math.max(0, offset - 50))}>Previous notes</button>
        <span className="text-xs text-slate-600">Page {Math.floor(offset / 50) + 1}</span>
        <button type="button" className="wp-button" disabled={busy || !hasMore}
          onClick={() => void readPage(offset + 50)}>Next notes</button>
      </nav>}
    </>}
    {error && state === 'READY' && <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
  </section>;
}

// ARTIFACT: ProjectNotesPanel.jsx
// VERSION: v1.0.0-EOS-SOURCE-BACKED-PROJECT-NOTES
// AUTHORITY BOUNDARY: EOS-validated source-backed project note reads/commands only
// TENANT POSTURE: exact tenant, principal, project and author, no fallback scope
// FAIL-CLOSED POSTURE: invalid responses, authorization and unavailable reads deny
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
