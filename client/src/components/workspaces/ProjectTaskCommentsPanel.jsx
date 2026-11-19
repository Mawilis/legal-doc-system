/**
 * TITLE: WILSY OS Source-Backed Project Task Discussion
 * VERSION: v1.6.1-BOUNDED-ACTIVITY-PAGINATION
 * AUTHORITY: Python EOS task collaboration comment and participation endpoints.
 * EPITOME: Read immutable task conversation pages and publish reviewed comments
 *          with explicit eligible participant mentions and durable EOS readback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/ProjectTaskCommentsPanel.jsx
 * COLLABORATION / OWNERSHIP: ProjectTasksPanel owns task selection; api.js
 *          transports the exact session; EOS owns command/audit/read authority.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.6.1-BOUNDED-ACTIVITY-PAGINATION retains
 *          independent bounded comment and task-event page controls, with
 *          source-verified offsets and no duplicate event-page injection into
 *          subsequent comment pages.
 * CHANGELOG: v1.6.0-VERIFIED-TASK-ACTIVITY-TIMELINE unifies
 *          bounded verified comment pages and immutable task lifecycle event
 *          pages in a newest-first activity display, with source-failure
 *          separation and governed links to approvals and attachments.
 *          No inferred events, unverified actors or fabricated totals.
 * CHANGELOG: v1.5.0-ONE-CLICK-DISCUSSION-READING makes a
 *          task's verified discussion immediately visible on Discuss, scrolls
 *          the selected conversation below fixed chrome, and moves the large
 *          composer/Markdown preview behind Write update. No extra click or
 *          scrolling through editor is required to read comments. EOS data,
 *          pagination, authority, draft and idempotent persistence stay intact.
 * CHANGELOG: v1.4.0-ON-DEMAND-VERIFIED-DISCUSSION keeps lengthy
 *          EOS discussion history collapsed until explicitly requested,
 *          exposes a verified current-page comment indicator and retains
 *          source-backed pagination, formatting and secure readback.
 * CHANGELOG: v1.3.2-BOUNDED-COMMENT-REJECTION-DETAIL surfaces strictly
 *          allowlisted EOS string validation codes separately from field-level
 *          422 details, preserving drafts, replay keys and privacy; never
 *          prints server-supplied arbitrary error text or user comment bodies.
 * CHANGELOG: v1.3.1-COMMENT-VALIDATION-EVIDENCE identifies
 *          only safe allowlisted HTTP 422 comment validation field names;
 *          preserves draft, command replay key and source reconciliation.
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
 * CHANGELOG: v1.6.1-BOUNDED-ACTIVITY-PAGINATION introduces task-threaded
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
  tenantHeaders, onClose, participantMode = false, onViewApprovals, onViewAttachments,
}) {
  const [items, setItems] = useState([]);
  const [events, setEvents] = useState([]);
  const [eventState, setEventState] = useState('LOADING');
  const [eventHasMore, setEventHasMore] = useState(false);
  const [eventOffset, setEventOffset] = useState(0);
  const [showComposer, setShowComposer] = useState(false);
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
  const discussionRef = useRef(null);
  const composerRef = useRef(null);
  const navigatedScope = useRef(null);
  const command = useRef({ fingerprint: '', key: '' });
  const route = '/projects/' + encodeURIComponent(projectId)
    + (participantMode ? '/my-project/tasks/' : '/tasks/')
    + encodeURIComponent(taskId) + '/comments';
  const eventRoute = '/projects/' + encodeURIComponent(projectId)
    + (participantMode ? '/my-project/tasks/' : '/tasks/')
    + encodeURIComponent(taskId) + '/events';
  const headers = tenantHeaders || {};

  const loadEvents = useCallback(async (nextOffset = 0) => {
    const active = scope;
    setEventState('LOADING');
    try {
      const { data } = await api.get(eventRoute + '?limit=50&offset=' + nextOffset, { headers });
      if (currentScope.current !== active) return;
      if (data?.schema !== 'WILSY-PROJECT-TASK-EVENT-LIST/V1'
        || data.tenant_id !== tenantId || data.principal_id !== principalId
        || data.project_id !== projectId || data.task_id !== taskId
        || data.limit !== 50 || data.offset !== nextOffset || typeof data.has_more !== 'boolean'
        || !Array.isArray(data.items) || data.items.length > 50
        || data.next_offset !== (data.has_more ? nextOffset + data.items.length : null)
        || data.items.some(entry => entry.schema !== 'wilsy.project.task.event.v1'
          || entry.tenant_id !== tenantId || entry.project_id !== projectId || entry.task_id !== taskId
          || !Number.isSafeInteger(entry.revision) || entry.revision < 1
          || !['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CANCELLED'].includes(entry.status_after)
          || !['PROJECT_TASK_CREATED', 'PROJECT_TASK_REVISED', 'PROJECT_TASK_TRANSITIONED'].includes(entry.event_type)
          || typeof entry.actor_principal_id !== 'string' || !entry.actor_principal_id
          || typeof entry.occurred_at !== 'string' || !Number.isFinite(Date.parse(entry.occurred_at)))
        || new Set(data.items.map(entry => entry.revision)).size !== data.items.length) {
        throw new Error('TASK_ACTIVITY_SOURCE_INVALID');
      }
      setEvents(data.items);
      setEventOffset(nextOffset);
      setEventHasMore(data.has_more);
      setEventState('READY');
    } catch {
      if (currentScope.current !== active) return;
      setEvents([]);
      setEventHasMore(false);
      setEventState('UNAVAILABLE');
    }
  }, [scope, eventRoute, tenantHeaders, tenantId, principalId, projectId, taskId]);

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
    setEvents([]);
    setEventState('LOADING');
    setEventHasMore(false);
    setEventOffset(0);
    setShowComposer(false);
    navigatedScope.current = null;
    setBody('');
    setMentions([]);
    setOffset(0);
    setHasMore(false);
    command.current = { fingerprint: '', key: '' };
    void load(0);
    void loadEvents();
    return () => { generation.current += 1; };
  }, [scope, load, loadEvents]);

  useEffect(() => {
    if (state !== 'READY' || navigatedScope.current === scope) return;
    navigatedScope.current = scope;
    discussionRef.current?.scrollIntoView?.({ behavior: 'auto', block: 'start' });
  }, [state, scope]);

  useEffect(() => {
    if (showComposer && state === 'READY') {
      composerRef.current?.scrollIntoView?.({ behavior: 'auto', block: 'start' });
    }
  }, [showComposer, state]);

  const activity = [
    ...items.map(item => ({
      id: 'comment:' + item.comment_id, type: 'comment',
      time: item.created_at, actor: item.author_principal_id, item,
    })),
    ...(eventState === 'READY' ? events.map(item => ({
      id: 'event:' + item.revision, type: 'event',
      time: item.occurred_at, actor: item.actor_principal_id, item,
    })) : []),
  ].sort((a, b) => (Date.parse(b.time) || 0) - (Date.parse(a.time) || 0)
    || a.id.localeCompare(b.id));
  const displayTime = value => Number.isFinite(Date.parse(value))
    ? new Date(value).toLocaleString() : 'Timestamp not verified';
  const displayActor = id => id === principalId ? 'You (authenticated author)'
    : 'Verified principal · ' + String(id).slice(0, 12) + '…';

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
      const validation = Array.isArray(cause?.response?.data?.detail)
        ? cause.response.data.detail : [];
      const safeFields = [...new Set(validation.flatMap(problem => Array.isArray(problem?.loc)
        ? problem.loc.filter(field => field === 'body' || field === 'mentions') : []))];
      const detail = cause?.response?.data?.detail;
      const safeCodes = {
        PROJECT_NOTE_IDEMPOTENCY_KEY_INVALID: 'The command key was rejected. Do not retry until the request is reconciled.',
        PROJECT_COMMENT_BODY_INVALID: 'Comment text was rejected by EOS content rules.',
        PROJECT_COMMENT_MENTIONS_INVALID: 'Mention references were rejected by EOS.',
      };
      const serverReason = typeof detail === 'string'
        && Object.prototype.hasOwnProperty.call(safeCodes, detail)
        ? safeCodes[detail] : null;
      setError(code === 403 ? 'EOS denied your task comment.'
        : code === 409 ? 'Mention eligibility or replay changed. Refresh and reconcile.'
          : code === 422 ? 'EOS rejected the comment input'
            + (safeFields.length ? ': ' + safeFields.join(', ') : '.')
            + (serverReason ? ' ' + serverReason : ' Inspect the safe validation detail in the failed network response.')
            + ' The draft remains intact; verify before retrying.'
            : 'EOS has not verified the comment. Check source state before retrying.');
    } finally {
      if (currentScope.current === active) setBusy(false);
    }
  };

  return <section ref={discussionRef} aria-label="Task discussion"
    className="mt-4 scroll-mt-28 rounded-xl border border-blue-200 bg-slate-50 p-3">
    <div className="flex items-center justify-between gap-3">
      <h4 className="flex items-center gap-2 font-semibold text-slate-900">
        <MessageSquare size={16}/> Activity &amp; discussion
      </h4>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="wp-button" disabled={busy}
          onClick={() => { void load(offset); void loadEvents(eventOffset); }}><RefreshCw size={14}/> Refresh</button>
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

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3"
        aria-label="Verified discussion availability">
        <div className="min-w-0">
          <h5 className="text-sm font-semibold text-slate-900">Source-verified activity</h5>
          <p role="status" className="mt-1 text-xs text-slate-600">
            {items.length > 0
              ? items.length + (hasMore ? '+ verified comments on this page' : ' verified comments')
              : 'No verified comments on this page'}
            {hasMore ? ' · More pages available' : ''}
          </p>
        </div>
        <button type="button" className="wp-button" aria-expanded={showComposer}
          aria-controls="task-comment-composer"
          onClick={() => setShowComposer(current => !current)}>
          {showComposer ? 'Close editor' : 'Write update'}
        </button>
      </div>
      {showComposer && <div id="task-comment-composer" ref={composerRef}
        className="scroll-mt-28">
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
      </div>}
      <div id="verified-task-comment-history" aria-label="Verified task comment history">
      <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
        <h5 className="text-sm font-semibold text-slate-900">Activity &amp; discussion · newest first</h5>
        <div className="flex flex-wrap gap-2">
          {typeof onViewApprovals === 'function' &&
            <button type="button" className="wp-button" onClick={onViewApprovals}>Decisions &amp; approvals</button>}
          {typeof onViewAttachments === 'function' &&
            <button type="button" className="wp-button" onClick={onViewAttachments}>Attachments &amp; evidence</button>}
        </div>
      </div>
      {eventState === 'UNAVAILABLE' && <p role="status" className="mt-2 text-sm text-amber-900">
        Task lifecycle evidence is unavailable. Verified comments remain readable; no missing events are inferred.
      </p>}
      {eventState === 'LOADING' && <p role="status" className="mt-2 text-sm text-slate-600">Verifying lifecycle evidence…</p>}
      <p className="mt-2 text-xs text-slate-600">Newest first across the two current verified source pages.
        {hasMore || eventHasMore ? ' Additional source pages exist; this is not the complete history.' : ''}
        {' '}Project Notes remain separate project-wide records.</p>
      <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
        {activity.map(entry => <li className="p-3 text-sm" key={entry.id}>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <strong className="break-words text-slate-900">
              {entry.type === 'comment' ? 'Progress update / comment'
                : entry.item.event_type === 'PROJECT_TASK_CREATED' ? 'Work created'
                  : entry.item.event_type === 'PROJECT_TASK_REVISED' ? 'Work revised'
                    : 'Lifecycle transition'}
            </strong>
            <time className="text-xs text-slate-600" dateTime={entry.time}>{displayTime(entry.time)}</time>
          </div>
          <p className="mt-1 text-xs text-slate-600" title={entry.actor}>
            By {displayActor(entry.actor)}
            {entry.type === 'event' ? ' · revision ' + entry.item.revision + ' · ' + entry.item.status_after.replaceAll('_', ' ').toLowerCase() : ''}
          </p>
          {entry.type === 'comment' && <div className="mt-2"><MarkdownText value={entry.item.body}/></div>}
          {entry.type === 'comment' && entry.item.mentions.length > 0 &&
            <p className="mt-1 break-words text-xs text-slate-600">Mentions: {entry.item.mentions.length} source references</p>}
        </li>)}
        {activity.length === 0 && eventState !== 'LOADING' && <li className="p-4 text-sm text-slate-600">
          No EOS-verified activity is available on these pages.
        </li>}
      </ul>
      {(eventOffset > 0 || eventHasMore) &&
        <nav aria-label="Task event pages" className="mt-3 flex items-center justify-between gap-2">
          <button type="button" className="wp-button" disabled={eventOffset === 0 || eventState === 'LOADING'}
            onClick={() => void loadEvents(Math.max(0, eventOffset - 50))}>Previous lifecycle events</button>
          <span className="text-xs text-slate-600">Lifecycle page {Math.floor(eventOffset / 50) + 1}</span>
          <button type="button" className="wp-button" disabled={!eventHasMore || eventState === 'LOADING'}
            onClick={() => void loadEvents(eventOffset + 50)}>Next lifecycle events</button>
        </nav>}
      {(offset > 0 || hasMore) &&
        <nav aria-label="Task comment pages" className="mt-2 flex items-center justify-between gap-2">
          <button className="wp-button" type="button" disabled={busy || offset === 0}
            onClick={() => void load(Math.max(0, offset - 50))}>Previous comments</button>
          <span className="text-xs text-slate-600">Page {Math.floor(offset / 50) + 1}</span>
          <button className="wp-button" type="button" disabled={busy || !hasMore}
            onClick={() => void load(offset + 50)}>Next comments</button>
        </nav>}

      </div>
      {error && <p role="alert" className="mt-2 text-sm text-rose-700">{error}</p>}
    </>}
  </section>;
}

// ARTIFACT: ProjectTaskCommentsPanel.jsx
// VERSION: v1.6.1-BOUNDED-ACTIVITY-PAGINATION
// AUTHORITY BOUNDARY: only EOS-authored comments; no notification dispatch
// TENANT POSTURE: exact tenant/principal/project/task and replay-scoped drafts
// FAIL-CLOSED POSTURE: malformed envelopes and missing mention choices deny
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
