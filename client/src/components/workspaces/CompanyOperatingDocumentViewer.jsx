/**
 * TITLE: WILSY OS Mission and Strategy Document Experience
 * VERSION: v1.1.0-LIVE-SESSION-SOURCE-STATUS
 * AUTHORITY: Python EOS owns content, publication, IAM and durable revision truth.
 * EPITOME: One accessible full-height document drawer for Mission and Strategy,
 *          including honest unpublished state and separately authorized review.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/CompanyOperatingDocumentViewer.jsx
 * COLLABORATION / OWNERSHIP: Headquarters opens the drawer; AuthContext supplies
 * current scope; companyOperatingDocumentsClient validates source contracts.
 * CERTIFICATION / UPDATE DATE: 2026-11-13
 * CHANGELOG: v1.1.0-LIVE-SESSION-SOURCE-STATUS distinguishes local authentication, denied access,
 * unavailable transport/source and invalid responses; presents useful recovery
 * and suppresses commands after an authorization or unverified source failure.
 * CHANGELOG: v1.0.1-FOUNDER-SUPPLIED-LOGO preserves the same selected square navy logo
 * used by authenticated Headquarters; source lifecycle and scope are unchanged.
 * CHANGELOG: v1.0.0-SOURCE-OWNED-COMPANY-DOCUMENT-VIEWER adds contents, publication
 * evidence, history, source-gated draft/submit/publish and verified readback.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; keyboard accessibility.
 * SECURITY / PRIVACY POSTURE: Plain React text only; no persisted draft, generated
 * policy, inferred objectives, raw diagnostics or credentials in DOM/logs.
 * TENANT BOUNDARY: Exact current tenant/principal/session and credential revision;
 * scope changes abort reads and suppress late results, drafts and receipts.
 * AUTHORITY BOUNDARY: UI actions never grant permission. Source endpoints
 * reauthorize every command; acknowledgement alone is not verified publication.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useCallback, useContext, useEffect, useRef, useState } from 'react';
import { ArrowLeft, ArrowUpRight, BookOpen, CheckCircle2, Clock3, FileText, History, Loader2, RefreshCw, ShieldCheck, X } from 'lucide-react';
import { createPortal } from 'react-dom';
import AuthContext from '../../contexts/authContext.jsx';
import { currentUnifiedMyWorkScope } from '../../services/unifiedMyWorkSync.js';
import { commandCompanyDocument, readCompanyDocumentHistory, readCompanyOperatingDocument } from '../../services/companyOperatingDocumentsClient.js';
import styles from './CompanyOperatingDocumentViewer.module.css';
import { WILSY_PLATFORM_LOGO_SRC } from '../os/wilsyDashboardChromeConfig.js';

const labelFor = classification => classification === 'MISSION' ? 'Our Mission' : 'Our Strategy';
const displayDate = value => value ? new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : 'Not effective';
const emptyProposal = () => ({ title: '', document_version: '', sections: [{ section_id: 'section-1', title: '', body: '' }] });
// The API has both FastAPI detail envelopes and institutional exception
// envelopes. Only bounded machine codes enter the UI; never server messages,
// credentials, exception stacks, arbitrary diagnostics or confidential bodies.
const sourceError = failure => {
  const status = Number.isInteger(failure?.response?.status) ? failure.response.status : null;
  const body = failure?.response?.data;
  const candidate = body?.detail?.error || body?.detail?.code || body?.error?.code || body?.code
    || (typeof body?.error === 'string' ? body.error : null) || failure?.code || failure?.message;
  const code = typeof candidate === 'string' && /^COMPANY_DOCUMENT_[A-Z_]{1,80}$/.test(candidate)
    ? candidate : status ? 'HTTP_' + status : 'COMPANY_DOCUMENT_CONNECTION_FAILED';
  const evidence = { code, status };
  if (status === 401 || code === 'COMPANY_DOCUMENT_AUTHENTICATED_SCOPE_REQUIRED') return {
    ...evidence, kind: 'AUTHENTICATION_REQUIRED', title: 'Sign-in verification required',
    message: 'The current company session must be verified before this document can be read.',
    next: 'Return to the sign-in screen if your session has expired. Once Headquarters confirms your current session, retry this read.',
  };
  if (status === 403) return {
    ...evidence, kind: 'ACCESS_DENIED', title: 'Access denied',
    message: 'EOS has not authorized this document operation for your current company capacity.',
    next: 'An authorized company administrator must verify document access through the existing IAM process. A Founder title alone does not grant document permission.',
  };
  if (status === 409) return {
    ...evidence, kind: 'CONFLICT', title: 'The document has changed',
    message: 'The source revision no longer matches the requested operation.',
    next: 'Refresh the current publication and review its latest source revision before retrying.',
  };
  if (status === 404 && code === 'COMPANY_DOCUMENT_NOT_FOUND') return {
    ...evidence, kind: 'REVISION_UNAVAILABLE', title: 'Revision unavailable',
    message: 'The requested revision is not available to your current company capacity.',
    next: 'Open the current publication or refresh permitted revision history. This result does not establish that no approved publication exists.',
  };
  if (code === 'COMPANY_DOCUMENT_RESPONSE_INVALID') return {
    ...evidence, kind: 'INVALID_RESPONSE', title: 'Document response could not be verified',
    message: 'The source response did not match the requested company, principal or publication contract.',
    next: 'Retry the source read. If verification still fails, share the status code below with support; no unverified content is displayed.',
  };
  return {
    ...evidence, kind: 'UNAVAILABLE', title: 'Document source unavailable',
    message: status === 404 ? 'The running service did not provide the company-document endpoint.'
      : status ? 'The company-document source could not complete a verified read.'
        : 'The company-document service could not be reached or did not return a response.',
    next: 'Retry the source read. If it remains unavailable, support must check the running EOS route, source connection and current company authorization. Publication status is unknown until a verified read succeeds.',
  };
};

/**
 * @description Open a current company document with contents and source-owned actions.
 * @collaboration Headquarters Mission/Strategy controls and canonical EOS document APIs.
 * @institutional Only source publication state labels official content. Drafts are
 * private to separately authorized users. Commands use stable retry keys and a
 * second source read before any success claim. No transaction or permission is
 * owned by this component; closing discards transient unsaved proposals.
 * @param {{classification:'MISSION'|'STRATEGY',onClose:Function,onOpenWork:Function}} props
 * @returns {JSX.Element} Accessible responsive source-backed document drawer.
 */
export default function CompanyOperatingDocumentViewer({ classification, onClose, onOpenWork }) {
  const auth = useContext(AuthContext) || {};
  const baseScope = currentUnifiedMyWorkScope(auth, auth.user?.tenantId);
  const credential = useRef({ token: auth.token, revision: 0 });
  if (credential.current.token !== auth.token) credential.current = { token: auth.token, revision: credential.current.revision + 1 };
  const sessionKey = baseScope ? baseScope + ':' + credential.current.revision : null;
  const epoch = useRef(sessionKey);
  epoch.current = sessionKey;
  const scope = { tenantId: auth.user?.tenantId, principalId: auth.user?.id };
  const [source, setSource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState('document');
  const [history, setHistory] = useState(null);
  const [query, setQuery] = useState({ review: false, revision: null });
  const queryRef = useRef(query);
  const [editorOpen, setEditorOpen] = useState(false);
  const [proposal, setProposal] = useState(emptyProposal);
  const [approvalReference, setApprovalReference] = useState('');
  const [effectiveFrom, setEffectiveFrom] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const readId = useRef(0);
  const readController = useRef(null);
  const commandLock = useRef(null);
  const retryKeys = useRef(new Map());
  const containerRef = useRef(null);
  const closeRef = useRef(null);
  const data = source?.scope === sessionKey && source?.classification === classification ? source.data : null;
  const currentHistory = history?.scope === sessionKey && history?.classification === classification ? history.data : null;
  const document = data?.document;
  const actions = !error && !loading ? data?.available_actions || [] : [];
  const active = key => epoch.current === key && key !== null;

  const load = useCallback(async (nextQuery = queryRef.current) => {
    const request = ++readId.current;
    const key = sessionKey;
    readController.current?.abort();
    const controller = new AbortController(); readController.current = controller;
    setLoading(true); setError(null); setSource(null); setHistory(null); setMessage('');
    if (!key) { setLoading(false); setError(sourceError({ code: 'COMPANY_DOCUMENT_AUTHENTICATED_SCOPE_REQUIRED' })); return; }
    try {
      const result = await readCompanyOperatingDocument(classification, scope, { token: auth.token, signal: controller.signal, ...nextQuery });
      if (!active(key) || request !== readId.current) return;
      setSource({ scope: key, classification, data: result });
    } catch (failure) {
      if (active(key) && request === readId.current && failure?.name !== 'AbortError' && failure?.name !== 'CanceledError') setError(sourceError(failure));
    } finally { if (active(key) && request === readId.current) setLoading(false); }
  }, [classification, sessionKey, auth.token]);

  useEffect(() => {
    epoch.current = sessionKey;
    const fresh = { review: false, revision: null };
    queryRef.current = fresh; setQuery(fresh); setHistory(null); setTab('document');
    setEditorOpen(false); setProposal(emptyProposal()); setApprovalReference(''); setEffectiveFrom('');
    setMessage(''); setBusy(false); retryKeys.current.clear(); commandLock.current = null;
    void load(fresh);
    return () => { readId.current += 1; readController.current?.abort(); epoch.current = null; };
  }, [load]);

  useEffect(() => {
    const trigger = window.document.activeElement;
    const formerOverflow = window.document.body.style.overflow;
    window.document.body.style.overflow = 'hidden'; closeRef.current?.focus();
    return () => { window.document.body.style.overflow = formerOverflow; trigger?.focus?.(); };
  }, []);

  const changeQuery = next => {
    queryRef.current = next; setQuery(next); setTab('document'); setEditorOpen(false); setHistory(null);
    void load(next);
  };
  const openHistory = async () => {
    if (!sessionKey || busy) return;
    const key = sessionKey; const request = ++readId.current;
    readController.current?.abort(); const controller = new AbortController(); readController.current = controller;
    setTab('history'); setLoading(true); setError(null); setHistory(null);
    try {
      const result = await readCompanyDocumentHistory(classification, scope, { token: auth.token, signal: controller.signal, review: query.review });
      if (active(key) && request === readId.current) setHistory({ scope: key, classification, data: result });
    } catch (failure) { if (active(key) && request === readId.current && failure?.name !== 'CanceledError' && failure?.name !== 'AbortError') setError(sourceError(failure)); }
    finally { if (active(key) && request === readId.current) setLoading(false); }
  };
  const perform = async (action, payload) => {
    if (!sessionKey || commandLock.current || !data || !actions.includes(action)) return;
    const key = sessionKey; const commandToken = Symbol(action); commandLock.current = commandToken;
    const intent = JSON.stringify([classification, action, payload]);
    if (!retryKeys.current.has(intent)) {
      if (typeof globalThis.crypto?.randomUUID !== 'function') { commandLock.current = null; setError(sourceError(null)); return; }
      retryKeys.current.set(intent, globalThis.crypto.randomUUID());
    }
    setBusy(true); setMessage(''); setError(null);
    let acknowledged = false;
    try {
      const receipt = await commandCompanyDocument(classification, scope, action, payload, retryKeys.current.get(intent), { token: auth.token });
      acknowledged = true;
      if (!active(key) || commandLock.current !== commandToken) return;
      const next = { review: true, revision: null };
      readController.current?.abort(); const controller = new AbortController(); readController.current = controller;
      const readback = await readCompanyOperatingDocument(classification, scope, { token: auth.token, signal: controller.signal, ...next });
      if (readback.document?.revision !== receipt.revision || readback.document?.fingerprint !== receipt.fingerprint) throw new Error('COMPANY_DOCUMENT_READBACK_UNVERIFIED');
      if (!active(key) || commandLock.current !== commandToken) return;
      readId.current += 1; queryRef.current = next; setQuery(next); setSource({ scope: key, classification, data: readback });
      setEditorOpen(false); setHistory(null); setTab('document'); retryKeys.current.delete(intent);
      setMessage('EOS confirmed the command and its durable document readback.');
    } catch (failure) {
      if (!active(key) || commandLock.current !== commandToken) return;
      setError(acknowledged ? { ...sourceError(failure), kind: 'READBACK_UNVERIFIED', title: 'Command recorded; current readback unverified', message: 'No updated publication is claimed. Refresh the source to verify the recorded revision before another command.' } : sourceError(failure));
    } finally { if (active(key) && commandLock.current === commandToken) { commandLock.current = null; setBusy(false); } }
  };
  const trapKeyboard = event => {
    if (event.key === 'Escape') { event.stopPropagation(); onClose(); }
    if (event.key !== 'Tab') return;
    const nodes = [...containerRef.current.querySelectorAll('button:not([disabled]),input:not([disabled]),textarea:not([disabled]),select:not([disabled]),a[href]')]
      .filter(node => node.getClientRects().length > 0);
    const first = nodes[0]; const last = nodes[nodes.length - 1];
    if (event.shiftKey && window.document.activeElement === first) { event.preventDefault(); last?.focus(); }
    else if (!event.shiftKey && window.document.activeElement === last) { event.preventDefault(); first?.focus(); }
  };
  const publish = event => {
    event.preventDefault();
    const effective = new Date(effectiveFrom);
    if (!Number.isFinite(effective.getTime())) {
      setError({ kind: 'INVALID_DATE', code: 'COMPANY_DOCUMENT_EFFECTIVE_DATE_INVALID', status: null, title: 'A valid effective date is required', message: 'Choose when the independently approved document should become effective.', next: 'Refresh the source and enter a valid effective date before submitting approval.' });
      return;
    }
    void perform('PUBLISH', { expected_revision: data?.current_revision ?? 0,
      approval_reference: approvalReference, effective_from: effective.toISOString() });
  };
  const expected = data?.current_revision ?? 0;

  return createPortal(<div className={styles.backdrop} onMouseDown={event => { if (event.target === event.currentTarget) onClose(); }}>
    <section ref={containerRef} className={styles.viewer} role="dialog" aria-modal="true" aria-labelledby="company-document-title" data-company-document={classification} onKeyDown={trapKeyboard}>
      <header className={styles.header}><img src={WILSY_PLATFORM_LOGO_SRC} alt="WILSY OS logo"/><div><span>WILSY · COMPANY OPERATING DOCUMENTS</span><h1 id="company-document-title">{labelFor(classification)}</h1></div><button ref={closeRef} type="button" onClick={onClose} aria-label="Close company document"><X size={20}/></button></header>
      <div className={styles.toolbar}><button type="button" onClick={() => changeQuery({ review: false, revision: null })} disabled={busy}><ArrowLeft size={14}/> Current publication</button><button type="button" onClick={() => changeQuery(queryRef.current)} disabled={loading || busy}><RefreshCw size={14} className={loading ? styles.spin : ''}/> Refresh source</button><button type="button" onClick={openHistory} disabled={busy || !sessionKey || !data || loading || Boolean(error)}><History size={14}/> Revision history</button><button type="button" onClick={onOpenWork}><ArrowUpRight size={14}/> My Work</button></div>
      <div className={styles.body}>
        <aside className={styles.contents} aria-label="Document contents"><p>CONTENTS</p>{document && !error && !loading && tab === 'document' ? document.sections.map(section => <button type="button" key={section.section_id} onClick={() => containerRef.current.querySelector('[data-document-section="' + section.section_id + '"]')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>{section.title}</button>) : <span>Publication overview</span>}<div className={styles.sourceBoundary}><ShieldCheck size={18}/><strong>Source-owned publication</strong><p>Preparation and submission are distinct from independent approval.</p></div></aside>
        <div className={styles.scroll}>
          {message && <p className={styles.success} role="status"><CheckCircle2 size={16}/>{message}</p>}
          {error && <section className={styles.notice} role="alert" data-document-state={error.kind}>
            <ShieldCheck size={28} aria-hidden="true"/><h2>{error.title}</h2><p>{error.message}</p>
            <dl className={styles.sourceStatus} aria-label="Document source status">
              <div><dt>Requested document</dt><dd>{labelFor(classification)}</dd></div>
              <div><dt>Publication source</dt><dd>/api/company-operating-documents/{classification}</dd></div>
              <div><dt>Operation status</dt><dd>{error.status ? 'HTTP ' + error.status : error.kind === 'AUTHENTICATION_REQUIRED' ? 'Not sent · current session required' : 'No verified response'}</dd></div>
              <div><dt>Reference</dt><dd>{error.code}</dd></div>
            </dl>
            <h3>Next step</h3><p>{error.next}</p>
            <button type="button" onClick={() => changeQuery({ review: false, revision: null })} disabled={busy}>Retry source read</button>
            <p className={styles.boundaryNote}>Company document access and publication are governed independently. Preparation requires author permission; publication requires a different authorized approver.</p>
          </section>}
          {loading ? <div className={styles.loading} role="status"><Loader2 className={styles.spin} size={24}/> Loading the authorized document source…</div>
            : error ? null : tab === 'history' ? <section className={styles.paper}><h2>Revision history</h2><p>Only revisions permitted for your current company capacity appear here.</p>{currentHistory?.items.length ? currentHistory.items.map(item => <button className={styles.revisionRow} key={item.revision} type="button" onClick={() => changeQuery({ review: query.review, revision: item.revision })}><FileText size={18}/><span><strong>Version {item.document_version} · revision {item.revision}</strong><small>{item.state} · {displayDate(item.recorded_at)}</small></span><ArrowUpRight size={15}/></button>) : !error && <p>No permitted revisions are available.</p>}</section>
              : data && <>
                <div className={styles.publication}><span className={styles.state} data-state={data.state}>{data.state === 'NOT_YET_PUBLISHED' ? 'NOT YET PUBLISHED' : data.state}</span>{query.review && <span>Authorized private review</span>}{document?.state === 'PUBLISHED' && Date.parse(document.effective_from) > Date.parse(data.as_of) && <span>Scheduled · not yet effective</span>}{query.revision && <span>Historical revision {query.revision}</span>}</div>
                {!document ? <section className={styles.unpublished} data-document-state="NOT_YET_PUBLISHED"><BookOpen size={34}/><span className={styles.state}>VERIFIED SOURCE · NO APPROVED PUBLICATION</span><h2>Not yet published</h2><p>The verified company source currently has no approved {classification === 'MISSION' ? 'Mission' : 'Strategy'} publication available for this view. An authorized author may prepare a private draft; a different authorized approver must publish it before it becomes official.</p><p className={styles.boundaryNote}>{actions.includes('CREATE_DRAFT') ? 'Your current source permission permits draft preparation below.' : 'Draft preparation and publication controls appear only when EOS authorizes them for your current capacity.'}</p></section>
                  : <article className={styles.paper}><div className={styles.documentIdentity}><span>{classification} · SOURCE VERSION {document.document_version}</span><h2>{document.title}</h2><dl><div><dt>Prepared by</dt><dd>{document.author_principal_id}</dd></div><div><dt>Effective date</dt><dd>{displayDate(document.effective_from)}</dd></div>{document.approved_by_principal_id && <div><dt>Approved / published by</dt><dd>{document.approved_by_principal_id}</dd></div>}{document.approval_reference && <div><dt>Approval reference</dt><dd>{document.approval_reference}</dd></div>}</dl></div>{document.sections.map(section => <section className={styles.documentSection} data-document-section={section.section_id} key={section.section_id}><h3>{section.title}</h3><p>{section.body}</p></section>)}<footer className={styles.fingerprint}><span>Source evidence · SHA3-512</span><code>{document.fingerprint}</code></footer></article>}
                <section className={styles.execution}><h2>Business execution</h2><p>The document source does not yet publish governed objective, project or work-item relationships. No owners, objectives or progress percentages are inferred.</p><button type="button" onClick={onOpenWork}>Open current My Work <ArrowUpRight size={14}/></button></section>
                <div className={styles.actions}>{actions.includes('REVIEW_DRAFTS') && <button type="button" disabled={busy} onClick={() => changeQuery({ review: true, revision: null })}>Review drafts</button>}{actions.includes('CREATE_DRAFT') && <button type="button" disabled={busy} onClick={() => { setProposal(emptyProposal()); setEditorOpen(true); }}>Prepare draft</button>}{actions.includes('SUBMIT') && <button type="button" disabled={busy} onClick={() => perform('SUBMIT', { expected_revision: expected })}>{busy ? 'Verifying…' : 'Submit for approval'}</button>}</div>
                {editorOpen && actions.includes('CREATE_DRAFT') && <form className={styles.form} onSubmit={event => { event.preventDefault(); void perform('CREATE_DRAFT', { ...proposal, expected_revision: expected }); }}><h2>Prepare a proposed {classification === 'MISSION' ? 'Mission' : 'Strategy'}</h2><p>This remains a private draft. A different authorized publisher must approve it.</p><label>Document title<input required maxLength={200} value={proposal.title} onChange={event => setProposal({ ...proposal, title: event.target.value })}/></label><label>Document version<input required pattern="[0-9]+\.[0-9]+\.[0-9]+" value={proposal.document_version} onChange={event => setProposal({ ...proposal, document_version: event.target.value })}/></label>{proposal.sections.map((section, index) => <fieldset key={section.section_id}><legend>Section {index + 1}</legend><label>Section title<input required maxLength={160} value={section.title} onChange={event => setProposal({ ...proposal, sections: proposal.sections.map((item,i) => i === index ? { ...item, title: event.target.value } : item) })}/></label><label>Proposed content<textarea required maxLength={20000} value={section.body} onChange={event => setProposal({ ...proposal, sections: proposal.sections.map((item,i) => i === index ? { ...item, body: event.target.value } : item) })}/></label></fieldset>)}<div className={styles.actions}><button type="button" disabled={busy || proposal.sections.length >= 24} onClick={() => setProposal({ ...proposal, sections: [...proposal.sections, { section_id: 'section-' + (proposal.sections.length + 1), title: '', body: '' }] })}>Add section</button><button type="submit" disabled={busy}>{busy ? 'Verifying…' : 'Save private draft'}</button><button type="button" onClick={() => setEditorOpen(false)} disabled={busy}>Cancel draft editor</button></div></form>}
                {actions.includes('PUBLISH') && <form className={styles.form} onSubmit={publish}><h2>Independent approval and publication</h2><p>Your current source permission and a different author are verified again by EOS.</p><label>Approval reference<input required maxLength={500} value={approvalReference} onChange={event => setApprovalReference(event.target.value)}/></label><label>Effective date and time<input required type="datetime-local" value={effectiveFrom} onChange={event => setEffectiveFrom(event.target.value)}/></label><button type="submit" disabled={busy}>{busy ? 'Verifying…' : 'Approve and publish'}</button></form>}
              </>}
        </div>
      </div>
      <footer className={styles.footer}><span><Clock3 size={13}/> {loading ? 'Verifying current company document source' : error ? error.kind === 'AUTHENTICATION_REQUIRED' ? 'Company session verification required' : error.kind === 'ACCESS_DENIED' ? 'Document access denied by EOS' : 'Document source not verified' : data ? 'Source verified ' + displayDate(data.as_of) : 'No verified source read'}</span><button type="button" onClick={onClose}>Close document</button></footer>
    </section>
  </div>, window.document.body);
}

// ARTIFACT: CompanyOperatingDocumentViewer.jsx
// VERSION: v1.1.0-LIVE-SESSION-SOURCE-STATUS
// AUTHORITY BOUNDARY: Source-backed content and command presentation only.
// TENANT POSTURE: Exact session/credential scope; transient state discarded on change.
// FAIL-CLOSED POSTURE: No official content or success without source/readback proof.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
