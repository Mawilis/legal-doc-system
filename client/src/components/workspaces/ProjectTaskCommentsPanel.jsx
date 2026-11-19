/**
 * TITLE: WILSY OS Source-Backed Project Task Discussion
 * VERSION: v1.3.0-SAFE-LIVE-MARKDOWN-DISCUSSION
 * AUTHORITY: Python EOS task collaboration comment and participation endpoints.
 * EPITOME: Read immutable task conversation pages and publish reviewed comments
 *          with explicit eligible participant mentions and durable EOS readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTaskCommentsPanel.jsx
 * COLLABORATION / OWNERSHIP: ProjectTasksPanel owns task selection; api.js
 *          transports the exact session; EOS owns command/audit/read authority.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.3.0-SAFE-LIVE-MARKDOWN-DISCUSSION renders source-owned
 *          discussion Markdown safely as React text nodes (never raw HTML),
 *          and provides immediate live formatting preview while editing;
 *          preserving 5000-character EOS payload, mentions, idempotency,
 *          immutable comment audit, readback and pagination unchanged.
 * CHANGELOG: v1.2.0-DISCUSSION-COMPOSER-FIRST places the
 *          EOS comment composer above the paginated conversation so entry
 *          stays accessible even with many comments, without changing EOS
 *          comment evidence, write authority or source pagination.
 * CHANGELOG: v1.1.0-PARTICIPANT-THREAD-ROUTE-ISOLATION uses
 *          separately authorized owner or participant task-thread routes;
 *          presentation never upgrades a participant to owner IAM.
 * CHANGELOG: v1.3.0-SAFE-LIVE-MARKDOWN-DISCUSSION introduces task-threaded
 *          discussion that does not infer notification dispatch or approvals.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: React escapes plain comment bodies; only sourced
 *          participant IDs can be explicitly selected as mentions.
 * TENANT BOUNDARY: Every list/result is checked against active exact tenant,
 *          project, task and principal; late prior session replies are ignored.
 * AUTHORITY BOUNDARY: UI never grants IAM/participation, task authority or
 *          approvals; EOS rechecks every mentioned principal on creation.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { LoaderCircle, MessageSquare, RefreshCw, Send, X } from 'lucide-react';
import api from '../../services/api.js';

const LIST = 'WILSY-PROJECT-COMMENT-LIST/V1';
const RESULT = 'WILSY-PROJECT-COMMENT-RESULT/V1';
const COMMENT = /^pcm-[a-f0-9]{48}$/;

function checkComment(value, tenantId, projectId, taskId) {
  return Boolean(
    value && value.schema === 'wilsy.project.comment.v1'
    && value.tenant_id === tenantId && value.project_id === projectId
    && value.task_id === taskId && COMMENT.test(value.comment_id)
    && typeof value.author_principal_id === 'string'
    && typeof value.body === 'string' && value.body.length > 0
    && Array.isArray(value.mentions) && value.mentions.length <= 10
    && value.mentions.every(person => typeof person === 'string' && person.length > 0)
    && /^[a-f0-9]{128}$/.test(value.fingerprint || ''),
  );
}

/**
 * Bounded plain-text Markdown projection; React escapes all content, including
 * attempted HTML. This is presentation only and never trusts remote markup.
 * Supports headings, paragraphs, bullets, ordered lists, bold, italic and code.
 * @authority EOS owns the unchanged Markdown source and comment audit.
 */
function MarkdownText({ value }) {
  const source = String(value || '').replace(/\r\n?/g, '\n');
  const inline = (line, prefix) => {
    const tokens = line.split(/(\*\*[^*\n]+\*\*|`[^`\n]+`|\*[^*\n]+\*)/g);
    return tokens.map((part, index) => {
      const key = prefix + ':' + index;
      if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
        return <strong key={key}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
        return <code key={key} className="rounded bg-slate-100 px-1 font-mono text-xs">{part.slice(1, -1)}</code>;
      }
      if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
        return <em key={key}>{part.slice(1, -1)}</em>;
      }
      return <React.Fragment key={key}>{part}</React.Fragment>;
    });
  };
  const elements = [];
  const lines = source.split('\n');
  for (let index = 0; index < lines.length;) {
    const line = lines[index];
    if (!line.trim()) { index += 1; continue; }
    const title = /^(#{1,3})\s+(.+)$/.exec(line);
    if (title) {
      elements.push(<h5 key={index} className="mt-2 font-bold text-slate-950">
        {inline(title[2], index)}</h5>);
      index += 1;
      continue;
    }
    const unordered = /^\s*[-*]\s+(.+)$/.exec(line);
    const ordered = /^\s*\d+\.\s+(.+)$/.exec(line);
    if (unordered || ordered) {
      const start = index;
      const entries = [];
      const expression = unordered ? /^\s*[-*]\s+(.+)$/ : /^\s*\d+\.\s+(.+)$/;
      while (index < lines.length && expression.test(lines[index])) {
        entries.push(<li key={index}>{inline(lines[index].replace(expression, '$1'), index)}</li>);
        index += 1;
      }
      const styling = 'ml-5 my-2 space-y-1 text-sm text-slate-900 ' + (unordered ? 'list-disc' : 'list-decimal');
      elements.push(unordered ? <ul key={start} className={styling}>{entries}</ul>
        : <ol key={start} className={styling}>{entries}</ol>);
      continue;
    }
    elements.push(<p key={index} className="my-2 whitespace-pre-wrap break-words text-sm leading-relaxed text-slate-900">
      {inline(line, index)}
    </p>);
    index += 1;
  }
  return <div className="min-w-0" data-testid="safe-markdown-discussion">{elements}</div>;
}

/** @description Source-owned comments with explicit bounded mentions. */
export default function ProjectTaskCommentsPanel({
  tenantId, projectId, principalId, taskId, participants,
  tenantHeaders, onClose, participantMode = false,
}) {
  const [items, setItems] = useState([]);
  const [body, setBody] = useState('');
  const [mentions, setMentions] = useState([]);
  const [state, setState] = useState('LOADING');
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const scope = [tenantId, principalId, projectId, taskId].join('\0');
  const currentScope = useRef(scope);
  currentScope.current = scope;
  const generation = useRef(0);
  const command = useRef({ fingerprint: '', key: '' });
  const route = '/projects/' + encodeURIComponent(projectId)
    + (participantMode ? '/my-project/tasks/' : '/tasks/')
    + encodeURIComponent(taskId) + '/comments';
  const headers = tenantHeaders || {};

  const load = useCallback(async (nextOffset = 0) => {
    const sequence = ++generation.current;
    const active = scope;
    setState(previous => previous === 'READY' ? 'REFRESHING' : 'LOADING');
    setError('');
    try {
      const { data } = await api.get(route + '?limit=50&offset=' + nextOffset, { headers });
      if (generation.current !== sequence || currentScope.current !== active) return false;
      if (
        data?.schema !== LIST || data.tenant_id !== tenantId
        || data.principal_id !== principalId || data.project_id !== projectId
        || data.task_id !== taskId || data.limit !== 50 || data.offset !== nextOffset
        || typeof data.has_more !== 'boolean'
        || !Array.isArray(data.items) || data.items.length > 50
        || data.next_offset !== (data.has_more ? nextOffset + data.items.length : null)
        || data.items.some(item => !checkComment(item, tenantId, projectId, taskId))
        || new Set(data.items.map(item => item.comment_id)).size !== data.items.length
      ) throw new Error('PROJECT_COMMENT_SOURCE_INVALID');
      setItems(data.items);
      setOffset(nextOffset);
      setHasMore(data.has_more);
      setState('READY');
      return true;
    } catch (cause) {
      if (generation.current !== sequence || currentScope.current !== active) return false;
      setItems([]);
      setHasMore(false);
      const code = cause?.response?.status;
      setError(code === 401 ? 'Sign in to read task comments.'
        : code === 403 ? 'EOS denied this task discussion.'
          : 'Comments could not be verified from EOS. Refresh to reconcile.');
      setState(code === 401 || code === 403 ? 'DENIED' : 'UNAVAILABLE');
      return false;
    }
  }, [scope, tenantId, principalId, projectId, taskId, route, tenantHeaders]);

  useEffect(() => {
    generation.current += 1;
    setItems([]);
    setBody('');
    setMentions([]);
    setOffset(0);
    setHasMore(false);
    command.current = { fingerprint: '', key: '' };
    void load(0);
    return () => { generation.current += 1; };
  }, [scope, load]);

  const submit = async event => {
    event.preventDefault();
    if (state !== 'READY' || busy) return;
    const text = body.trim();
    if (!text || text.length > 5000) return;
    if (mentions.some(person => !participants.some(item => item.principal_id === person))) {
      setError('Mention recipient is not in the verified project participant page.');
      return;
    }
    const fingerprint = JSON.stringify({ text, mentions });
    if (!command.current.key || command.current.fingerprint !== fingerprint) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') {
        setError('Cannot establish a durable command key in this browser session.');
        return;
      }
      command.current = { fingerprint, key: globalThis.crypto.randomUUID() };
    }
    const active = scope;
    setBusy(true);
    setError('');
    try {
      const { data } = await api.post(route, { body: text, mentions }, {
        headers: { ...headers, 'Idempotency-Key': command.current.key },
      });
      if (currentScope.current !== active) return;
      if (
        data?.schema !== RESULT || data.tenant_id !== tenantId
        || data.principal_id !== principalId || data.project_id !== projectId
        || data.task_id !== taskId
        || !checkComment(data.comment, tenantId, projectId, taskId)
      ) throw new Error('PROJECT_COMMENT_RESULT_INVALID');
      const verified = await load(0);
      if (!verified || currentScope.current !== active) return;
      command.current = { fingerprint: '', key: '' };
      setBody('');
      setMentions([]);
    } catch (cause) {
      if (currentScope.current !== active) return;
      const code = cause?.response?.status;
      setError(code === 403 ? 'EOS denied your task comment.'
        : code === 409 ? 'Mention eligibility or replay changed. Refresh and reconcile.'
          : 'EOS has not verified the comment. Check source state before retrying.');
    } finally {
      if (currentScope.current === active) setBusy(false);
    }
  };

  return <section aria-label="Task discussion" className="mt-4 rounded-xl border border-blue-200 bg-slate-50 p-3">
    <div className="flex items-center justify-between gap-3">
      <h4 className="flex items-center gap-2 font-semibold text-slate-900">
        <MessageSquare size={16}/> Task discussion
      </h4>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="wp-button" disabled={busy}
          onClick={() => void load(offset)}><RefreshCw size={14}/> Refresh</button>
        <button type="button" className="wp-button" disabled={busy}
          onClick={onClose} aria-label="Close task discussion"><X size={14}/> Close</button>
      </div>
    </div>
    {(state === 'LOADING' || state === 'REFRESHING') &&
      <p role="status" className="mt-3 flex items-center gap-2 text-sm text-slate-600">
        <LoaderCircle size={14} className="animate-spin"/> Verifying conversation…
      </p>}
    {(state === 'DENIED' || state === 'UNAVAILABLE') &&
      <p role="alert" className="mt-3 text-sm text-rose-700">{error}</p>}
    {state === 'READY' && <>
      <form onSubmit={submit} className="mt-3 space-y-2 rounded-lg border border-blue-200 bg-white p-4">
        <label className="block text-sm font-semibold text-slate-800">Write a task comment
          <textarea aria-label="New task comment" required rows={5}
            maxLength={5000} value={body} onChange={event => setBody(event.target.value)}
            placeholder="Write a progress update. Use **bold**, *italic*, headings or lists."
            className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-3 text-sm font-normal text-slate-900"/>
        </label>
        <section aria-label="Live formatted comment preview" className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <h5 className="text-xs font-bold uppercase tracking-wide text-slate-700">Live formatted preview</h5>
            <span className="text-xs tabular-nums text-slate-600">{body.length} / 5000 characters</span>
          </div>
          {body.trim() ? <MarkdownText value={body}/> : <p className="text-sm text-slate-600">
            Formatted text will appear here as you type or paste.
          </p>}
        </section>
        <fieldset className="rounded-lg border border-slate-200 p-3">
          <legend className="px-1 text-xs font-semibold text-slate-800">Mention verified contributors (optional)</legend>
          <div className="grid max-h-32 gap-2 overflow-auto sm:grid-cols-2">
            {participants.filter(item => item.principal_id !== principalId).map(person =>
              <label className="flex items-center gap-2 break-all text-xs text-slate-800"
                key={person.principal_id}>
                <input type="checkbox" checked={mentions.includes(person.principal_id)}
                  disabled={!mentions.includes(person.principal_id) && mentions.length >= 10}
                  onChange={event => setMentions(list => event.target.checked
                    ? [...list, person.principal_id]
                    : list.filter(value => value !== person.principal_id))}/>
                {person.principal_id}
              </label>)}
          </div>
          <p className="mt-2 text-xs text-slate-500">A mention is a source reference, not a delivered notification.</p>
        </fieldset>
        <button className="wp-button wp-button-primary" type="submit"
          disabled={busy || !body.trim()}><Send size={14}/> Publish to EOS</button>
      </form>
      <h5 className="mt-5 text-sm font-semibold text-slate-900">Verified discussion history · page {Math.floor(offset / 50) + 1}</h5>
      <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
        {items.map(item => <li className="p-3 text-sm" key={item.comment_id}>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <strong className="break-all text-slate-800">{item.author_principal_id}</strong>
            <time className="text-xs text-slate-500" dateTime={item.created_at}>{item.created_at}</time>
          </div>
          <div className="mt-2"><MarkdownText value={item.body}/></div>
          {item.mentions.length > 0 &&
            <p className="mt-1 break-words text-xs text-slate-600">Mentioned: {item.mentions.join(', ')}</p>}
        </li>)}
        {items.length === 0 && <li className="p-4 text-sm text-slate-600">
          No EOS comments for this task on this page.
        </li>}
      </ul>
      {(offset > 0 || hasMore) &&
        <nav aria-label="Task comment pages" className="mt-2 flex items-center justify-between gap-2">
          <button className="wp-button" type="button" disabled={busy || offset === 0}
            onClick={() => void load(Math.max(0, offset - 50))}>Previous comments</button>
          <span className="text-xs text-slate-600">Page {Math.floor(offset / 50) + 1}</span>
          <button className="wp-button" type="button" disabled={busy || !hasMore}
            onClick={() => void load(offset + 50)}>Next comments</button>
        </nav>}

      {error && <p role="alert" className="mt-2 text-sm text-rose-700">{error}</p>}
    </>}
  </section>;
}

// ARTIFACT: ProjectTaskCommentsPanel.jsx
// VERSION: v1.3.0-SAFE-LIVE-MARKDOWN-DISCUSSION
// AUTHORITY BOUNDARY: only EOS-authored comments; no notification dispatch
// TENANT POSTURE: exact tenant/principal/project/task and replay-scoped drafts
// FAIL-CLOSED POSTURE: malformed envelopes and missing mention choices deny
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
