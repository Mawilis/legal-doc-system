/**
 * TITLE: WILSY OS Institutional Legal Admission Operating Shell
 * VERSION: v1.8.0-RECORD-NAVIGATION-SCROLL-RESET
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Provides an operational legal-control workspace with collapsible
 *           system context, compact records, document focus, and explicit
 *           server-bound evidence commands.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/LegalAcceptanceGate.jsx
 * COLLABORATION / OWNERSHIP: Python legal_acceptance_router/service owns all
 *                            legal truth; this component owns presentation only.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: v1.8.0 resets the bounded document reading surface to its top
 *            whenever focus moves to a different server record, including
 *            Previous, Next, and Next unresolved navigation. The reset is
 *            presentation-only and never alters legal evidence or authority.
 *            v1.7.0 keeps the acted-on record in focus after POST plus
 *            status refresh confirmation, exposes server-confirmed feedback,
 *            and prevents repeat mutation while confirmation is unavailable.
 *            v1.6.1 center-aligns the server-issued document prose inside
 *            the bounded reading column without changing its legal meaning.
 *            v1.6.0 keeps the reader centred at the md desktop boundary,
 *            moves the command dock out of the bottom flow, caps mobile dock
 *            height, and keeps the status bar outside the reading scrollport.
 *            v1.5.0 made document focus a viewport-owned workspace with an
 *            820px reader, 280px command dock, OS status bar, low-chrome
 *            separators, compact metrics, and a non-card rail spine.
 *            v1.4.0 introduced the interaction shell.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Only server-issued document identity is posted;
 *                             UX state never creates legal or acceptance truth.
 * TENANT BOUNDARY: Displays only the authenticated server-issued plan.
 * AUTHORITY BOUNDARY: Client presentation and transport only; EOS owns legal
 *                     status, evidence, identity, and workspace release.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial
 *                                execution and settlement.
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Loader2,
  LockKeyhole,
  Menu,
  ShieldCheck,
  X,
} from 'lucide-react';
import api from '@/services/api';

const newIdempotencyKey = () => (
  typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `legal-${Date.now()}-${Math.random().toString(16).slice(2)}`
);

const evidenceMethodFor = (document) => (
  document?.agreementType === 'INSTITUTIONAL_CHARTER' ? 'ACKNOWLEDGEMENT' : 'ACCEPTANCE'
);

const actionLabelFor = (document) => (
  evidenceMethodFor(document) === 'ACKNOWLEDGEMENT' ? 'Record acknowledgement' : 'Record acceptance'
);

const formatDate = (value) => {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? '—'
    : date.toLocaleDateString('en-ZA', { year: 'numeric', month: '2-digit', day: '2-digit' });
};

const recordTypeFor = (document) => String(document?.agreementType || 'LEGAL_RECORD').replaceAll('_', ' ');

const isIntegrityBlocked = (document) => {
  if (!document) return false;
  const state = String(document.integrityState || document.integrityStatus || document.authorityIntegrity || '').toUpperCase();
  return document.integrityBlocked === true
    || ['BLOCKED', 'CORRUPT', 'REVIEW_REQUIRED', 'INTEGRITY_REVIEW_REQUIRED'].includes(state)
    || (typeof document.status === 'string' && document.status !== 'APPROVED')
    // The current stale Charter exposes its review marker in server content.
    || String(document.content || '').includes('DRAFT_REVIEW_REQUIRED')
    || /has not been approved/i.test(String(document.content || ''));
};

const diagnosticFor = (requestError, fallback) => {
  const response = requestError?.response;
  const detail = response?.data?.detail;
  return {
    title: fallback,
    detail: typeof detail === 'string' ? detail : 'SERVER_DETAIL_UNAVAILABLE',
    status: response?.status || null,
  };
};

function Compartment({ label, value, mono = false }) {
  return <span className="inline-flex min-h-7 items-center gap-1.5 px-1.5 py-1"><span className="text-[8px] font-bold tracking-[0.14em] text-stone-600">{label}</span><span className={`${mono ? 'font-mono ' : ''}text-[9px] text-stone-300`}>{value}</span></span>;
}

function SystemBar({ plan, recordedCount, total, railCollapsed, mobileRailOpen, onToggleRail, focusMode }) {
  return (
    <header className="flex min-h-[56px] shrink-0 flex-wrap items-center justify-between gap-2 border-b border-white/[0.08] bg-[#090b0a] px-3 py-2 text-stone-100 sm:px-5">
      <div className="flex min-w-0 items-center gap-2.5">
        <div className="grid h-7 w-7 shrink-0 place-items-center border border-[#d4af37]/45 bg-[#d4af37]/[0.06]" aria-hidden="true"><ShieldCheck className="h-4 w-4 text-[#d4af37]" /></div>
        <div className="hidden min-w-0 sm:block"><p className="text-[10px] font-extrabold uppercase tracking-[0.22em] text-[#d4af37]">WILSY OS</p><p className="text-[8px] uppercase tracking-[0.15em] text-stone-600">{focusMode ? 'Legal record' : 'Legal control'}</p></div>
      </div>
      <div className="flex min-w-0 flex-1 flex-wrap items-center justify-center divide-x divide-white/[0.08] px-1">
        <Compartment label="TENANT" value={plan?.tenantId || '—'} mono />
        <Compartment label="SESSION" value="AUTHENTICATED" />
        <Compartment label="MODULE" value="LEGAL ADMISSION" />
      </div>
      <div className="flex shrink-0 items-center divide-x divide-white/[0.08]"><Compartment label="EVIDENCE" value={`${recordedCount} / ${total}`} mono /><Compartment label="WORKSPACE" value="SEALED" /><button type="button" aria-label={mobileRailOpen || (typeof window !== 'undefined' && window.innerWidth >= 768 && !railCollapsed) ? 'Collapse system rail' : 'Open system rail'} aria-expanded={mobileRailOpen || (typeof window !== 'undefined' && window.innerWidth >= 768 && !railCollapsed)} onClick={onToggleRail} className="ml-1.5 grid h-8 w-8 place-items-center border border-white/[0.14] text-stone-400 transition hover:border-[#d4af37]/60 hover:text-[#f0d477] motion-reduce:transition-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#d4af37]"><Menu className="h-4 w-4" aria-hidden="true" /></button></div>
    </header>
  );
}

const railRows = (plan, recordedCount, total, remainingCount) => [
  ['IDENTITY', 'Authenticated'], ['TENANT', plan?.tenantId || 'Pending'], ['LEGAL CONTROL', plan?.status || 'Resolving'], ['EVIDENCE', `${recordedCount} / ${total} recorded`], ['WORKSPACE', 'Sealed'], ['SESSION', 'Bound'], ['REMAINING', `${remainingCount}`],
];

function RailRows({ plan, recordedCount, total, remainingCount, collapsed }) {
  return <div className="space-y-1">{railRows(plan, recordedCount, total, remainingCount).map(([label, value]) => <div key={label} title={`${label}: ${value}`} className={collapsed ? 'grid h-8 place-items-center text-[9px] font-bold text-stone-400' : 'border-b border-white/[0.055] px-2 py-2.5'}><span className={collapsed ? 'sr-only' : 'block text-[8px] font-bold tracking-[0.16em] text-stone-600'}>{label}</span>{collapsed ? <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-[#b99a45]" /> : <span className="mt-1 block break-words font-mono text-[10px] uppercase tracking-[0.05em] text-stone-300">{value}</span>}</div>)}</div>;
}

function SystemRail({ plan, recordedCount, total, remainingCount, collapsed, mobileOpen, onCloseMobile }) {
  return <>
    <aside data-testid="system-rail" aria-label="Admission system status" className={`${collapsed ? 'w-[54px]' : 'w-[220px]'} hidden shrink-0 border-r border-white/[0.06] bg-[#0a0c0b] px-2 py-4 transition-[width] duration-150 motion-reduce:transition-none md:block`}><p className={`${collapsed ? 'sr-only' : 'px-2'} mb-3 text-[9px] font-bold uppercase tracking-[0.18em] text-stone-600`}>System rail</p><RailRows plan={plan} recordedCount={recordedCount} total={total} remainingCount={remainingCount} collapsed={collapsed} />{!collapsed && <div className="mt-5 border-t border-white/[0.06] px-2 pt-3"><p className="text-[8px] font-bold uppercase tracking-[0.16em] text-[#b99a45]">Admission boundary</p><p className="mt-2 text-[10px] leading-5 text-stone-500">Server evidence is required before workspace release.</p></div>}</aside>
    {mobileOpen && <aside data-testid="mobile-system-rail" aria-label="Mobile admission system status" className="fixed inset-x-0 top-[56px] z-30 max-h-[calc(100dvh-56px)] overflow-y-auto border-b border-white/[0.12] bg-[#0a0c0b] p-4 shadow-2xl md:hidden"><div className="mb-3 flex items-center justify-between"><p className="text-[9px] font-bold uppercase tracking-[0.18em] text-stone-600">System rail</p><button type="button" aria-label="Close system rail" onClick={onCloseMobile} className="grid h-8 w-8 place-items-center border border-white/[0.12] text-stone-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d4af37]"><X className="h-4 w-4" /></button></div><RailRows plan={plan} recordedCount={recordedCount} total={total} remainingCount={remainingCount} collapsed={false} /></aside>}
  </>;
}

function StatusFooter({ plan, recordedCount, total }) {
  return <footer className="flex h-8 shrink-0 items-center gap-4 overflow-x-auto whitespace-nowrap border-t border-white/[0.08] px-3 text-[8px] font-bold uppercase tracking-[0.12em] text-stone-600 sm:px-5"><span>PYTHON EOS</span><span>TENANT <span className="font-mono text-stone-400">{plan?.tenantId || '—'}</span></span><span>SESSION AUTHENTICATED</span><span>EVIDENCE <span className="font-mono text-stone-400">{recordedCount}/{total}</span></span><span className="text-[#b99a45]">WORKSPACE SEALED</span></footer>;
}

function ShellFrame({ plan, recordedCount, total, remainingCount, railCollapsed, mobileRailOpen, onToggleRail, onCloseMobileRail, focusMode, children }) {
  return <div className="flex h-[100dvh] min-h-0 flex-col overflow-hidden bg-[#070908] text-stone-100"><SystemBar plan={plan} recordedCount={recordedCount} total={total} railCollapsed={railCollapsed} mobileRailOpen={mobileRailOpen} onToggleRail={onToggleRail} focusMode={focusMode} /><div className="flex min-h-0 flex-1"><SystemRail plan={plan} recordedCount={recordedCount} total={total} remainingCount={remainingCount} collapsed={railCollapsed} mobileOpen={mobileRailOpen} onCloseMobile={onCloseMobileRail} /><div className="min-h-0 min-w-0 flex-1">{children}</div></div><StatusFooter plan={plan} recordedCount={recordedCount} total={total} /></div>;
}

function ErrorSurface({ error, compact = false }) {
  if (!error) return null;
  return <div role="alert" className={`${compact ? 'mt-3' : 'mb-5'} flex items-start gap-3 border border-red-400/25 bg-red-400/[0.035] px-3 py-2.5 text-xs leading-5 text-red-200`}><AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-300" /><div><p className="text-[9px] font-bold uppercase tracking-[0.14em]">{error.title}</p><p className="mt-1 font-mono text-[10px] text-red-300">{error.detail}{error.status ? ` · HTTP ${error.status}` : ''}</p></div></div>;
}

function FocusMetadata({ document }) {
  return <dl className="grid grid-cols-2 gap-x-4 gap-y-2 border-y border-white/[0.08] py-3 text-[10px] sm:grid-cols-5"><div><dt className="text-[8px] font-bold tracking-[0.13em] text-stone-600">VERSION</dt><dd className="mt-1 font-mono text-stone-300">{document.version}</dd></div><div><dt className="text-[8px] font-bold tracking-[0.13em] text-stone-600">EFFECTIVE</dt><dd className="mt-1 font-mono text-stone-300">{formatDate(document.effectiveFrom)}</dd></div><div><dt className="text-[8px] font-bold tracking-[0.13em] text-stone-600">METHOD</dt><dd className="mt-1 font-bold uppercase text-[#b99a45]">{evidenceMethodFor(document)}</dd></div><div><dt className="text-[8px] font-bold tracking-[0.13em] text-stone-600">RECORD ID</dt><dd className="mt-1 break-all font-mono text-stone-300">{document.documentId}</dd></div><div><dt className="text-[8px] font-bold tracking-[0.13em] text-stone-600">EVIDENCE</dt><dd className={`mt-1 font-bold uppercase ${document.accepted ? 'text-emerald-300' : 'text-stone-300'}`}>{document.accepted ? 'RECORDED' : 'REQUIRED'}</dd></div></dl>;
}

function FocusAction({ document, submitting, recordEvidence, confirmationState }) {
  if (isIntegrityBlocked(document)) return <div role="alert" className="border border-amber-300/25 bg-amber-300/[0.045] px-3 py-3"><p className="text-[9px] font-bold uppercase tracking-[0.14em] text-amber-200">Integrity review required</p><p className="mt-1.5 text-[10px] leading-4 text-stone-400">Evidence recording unavailable for this server-issued record.</p></div>;
  if (document.accepted) return <div data-testid="evidence-recorded" aria-live="polite" className="flex items-start gap-2 border border-emerald-300/25 bg-emerald-300/[0.045] px-3 py-3 text-emerald-300"><CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" /><div><p className="text-[10px] font-bold uppercase tracking-[0.12em]">{evidenceMethodFor(document) === 'ACKNOWLEDGEMENT' ? 'Acknowledgement recorded' : 'Evidence recorded'}</p><p className="mt-1 text-[9px] font-bold uppercase tracking-[0.14em] text-emerald-200/80">Server confirmed</p></div></div>;
  if (confirmationState?.documentId === document.documentId) return <div data-testid="evidence-confirmation-pending" role="status" className="border border-amber-300/25 bg-amber-300/[0.045] px-3 py-3"><p className="text-[9px] font-bold uppercase tracking-[0.12em] text-amber-200">Evidence submitted</p><p className="mt-1 text-[9px] font-bold uppercase tracking-[0.12em] text-stone-400">{confirmationState.status === 'unavailable' ? 'Confirmation refresh unavailable' : 'Server confirmation pending'}</p></div>;
  return <button type="button" onClick={() => recordEvidence(document)} disabled={submitting === document.documentId} className="flex min-h-10 w-full items-center justify-center gap-2 border border-[#d4af37]/60 bg-[#d4af37] px-3 text-[10px] font-extrabold uppercase tracking-[0.1em] text-[#10110f] transition hover:bg-[#e0bd4a] disabled:cursor-not-allowed disabled:opacity-50 motion-reduce:transition-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#f3d66f]">{submitting === document.documentId ? <Loader2 className="h-4 w-4 animate-spin" /> : <LockKeyhole className="h-4 w-4" aria-hidden="true" />}{submitting === document.documentId ? 'Recording evidence…' : actionLabelFor(document)}</button>;
}

function CommandDeck({ document, index, total, submitting, recordEvidence, confirmationState, nextUnresolved, onNextUnresolved, onPrevious, onNext, onReturn, error }) {
  const serverRecorded = document.accepted;
  return <aside aria-label="Document command deck" data-testid="document-command-deck" className="flex min-h-0 max-h-[42dvh] shrink-0 flex-col overflow-y-auto border-t border-white/[0.06] px-4 py-4 md:max-h-none md:overflow-visible md:border-l md:border-t-0 md:px-5 md:py-5"><div className="flex items-center justify-between"><p className="text-[9px] font-bold uppercase tracking-[0.16em] text-[#b99a45]">Record</p><span className="font-mono text-[10px] text-stone-500">{index + 1} / {total}</span></div><div className="mt-4 border-b border-white/[0.06] pb-4"><p className="text-[8px] font-bold tracking-[0.14em] text-stone-600">CURRENT RECORD</p><h2 className="mt-2 text-sm font-semibold text-stone-100">{document.title}</h2><p className="mt-1 font-mono text-[9px] uppercase tracking-[0.06em] text-stone-600">{recordTypeFor(document)}</p></div><div className="grid grid-cols-2 gap-2 border-b border-white/[0.06] py-4"><Compartment label="STATE" value={serverRecorded ? 'RECORDED' : 'REQUIRED'} /><Compartment label="METHOD" value={evidenceMethodFor(document)} /></div><div className="mt-auto space-y-2 pt-4"><FocusAction document={document} submitting={submitting} recordEvidence={recordEvidence} confirmationState={confirmationState} />{serverRecorded ? (nextUnresolved ? <button type="button" aria-label="Next unresolved record" onClick={onNextUnresolved} className="flex min-h-9 w-full items-center justify-center gap-1 border border-[#d4af37]/60 px-2 text-[9px] font-bold uppercase tracking-[0.08em] text-[#f0d477] transition hover:bg-[#d4af37]/[0.08] motion-reduce:transition-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d4af37]">Next unresolved record <ChevronRight className="h-3.5 w-3.5" /></button> : null) : <div className="grid grid-cols-2 gap-2"><button type="button" aria-label="Previous record" onClick={onPrevious} disabled={index <= 0} className="flex min-h-9 items-center justify-center gap-1 border border-white/[0.13] px-2 text-[9px] font-bold uppercase text-stone-400 transition hover:text-stone-100 disabled:cursor-not-allowed disabled:opacity-35 motion-reduce:transition-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d4af37]"> <ChevronLeft className="h-3.5 w-3.5" /> Previous</button><button type="button" aria-label="Next record" onClick={onNext} disabled={index >= total - 1} className="flex min-h-9 items-center justify-center gap-1 border border-white/[0.13] px-2 text-[9px] font-bold uppercase text-stone-400 transition hover:text-stone-100 disabled:cursor-not-allowed disabled:opacity-35 motion-reduce:transition-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d4af37]">Next <ChevronRight className="h-3.5 w-3.5" /></button></div>}<button type="button" aria-label="Return to legal control" onClick={onReturn} className="flex min-h-9 w-full items-center justify-center gap-2 border border-white/[0.13] px-2 text-[9px] font-bold uppercase tracking-[0.1em] text-stone-400 transition hover:text-[#f0d477] motion-reduce:transition-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d4af37]"><ArrowLeft className="h-3.5 w-3.5" /> Return to legal control</button>{error && <ErrorSurface error={error} compact />}</div></aside>;
}

function DocumentFocusFrame({ plan, document, documents, index, submitting, error, confirmationState, nextUnresolved, onNextUnresolved, onReturn, onPrevious, onNext, recordEvidence }) {
  const readingSurfaceRef = useRef(null);

  useEffect(() => {
    const readingSurface = readingSurfaceRef.current;
    if (!readingSurface) return;
    readingSurface.scrollTo({ top: 0, left: 0, behavior: 'auto' });
  }, [document.documentId]);

  return (
    <main data-testid="document-focus-mode" className="flex h-full min-h-0 flex-col overflow-hidden">
      <div className="flex min-h-[64px] shrink-0 flex-wrap items-center justify-between gap-3 border-b border-white/[0.06] bg-[#0b0e0c] px-4 py-3 sm:px-6">
        <div className="min-w-0">
          <p className="text-[8px] font-bold uppercase tracking-[0.18em] text-[#b99a45]">Document focus · {recordTypeFor(document)}</p>
          <h1 className="mt-1 truncate text-lg font-semibold text-stone-100">{document.title}</h1>
          <p className="mt-1 font-mono text-[9px] text-stone-500">{document.version} · {formatDate(document.effectiveFrom)}</p>
        </div>
        <span className="text-[8px] font-bold uppercase tracking-[0.12em] text-stone-500">Server record</span>
      </div>
      <div data-testid="focus-workspace-grid" className="mx-auto grid w-full max-w-[1280px] min-h-0 flex-1 grid-rows-[minmax(0,1fr)_auto] overflow-hidden md:grid-cols-[minmax(0,880px)_280px] md:grid-rows-1 md:gap-6">
        <div
          ref={readingSurfaceRef}
          aria-label="Document reading surface"
          className="flex min-h-0 min-w-0 justify-center overflow-y-auto overscroll-contain px-4 py-5 sm:px-8 sm:py-7"
        >
          <article className="mx-auto w-full max-w-[860px]">
            <FocusMetadata document={document} />
            <details className="mt-3 text-[9px]">
              <summary className="inline-flex cursor-pointer list-none border border-white/[0.1] px-2.5 py-1.5 font-bold uppercase tracking-[0.12em] text-stone-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d4af37]">Canonical metadata</summary>
              <div className="mt-2 grid gap-1 border border-white/[0.08] bg-black/15 p-2.5 font-mono text-[9px] leading-4 text-stone-500">
                <span>DOCUMENT_ID · {document.documentId}</span>
                <span>SHA3-512 · {document.sha3_512 || '—'}</span>
              </div>
            </details>
            <div data-testid="legal-document-content" tabIndex="0" className="select-text whitespace-pre-wrap py-7 text-center text-base leading-[1.75] text-stone-200 outline-none focus-visible:ring-1 focus-visible:ring-[#d4af37]/60">
              {document.content || 'No document text was supplied by the server.'}
            </div>
          </article>
        </div>
        <CommandDeck
          document={document}
          index={index}
          total={documents.length}
          submitting={submitting}
          recordEvidence={recordEvidence}
          confirmationState={confirmationState}
          nextUnresolved={nextUnresolved}
          onNextUnresolved={onNextUnresolved}
          onPrevious={onPrevious}
          onNext={onNext}
          onReturn={onReturn}
          error={error}
        />
      </div>
    </main>
  );
}

/**
 * Render the server-derived acceptance plan as an operational control plane.
 * @param {{onComplete?: () => void, initialPlan?: object|null}} props
 * @returns {React.ReactElement} Fail-closed legal admission workspace.
 * @collaboration Consumes GET/POST /api/legal-acceptance and notifies App.
 * @institutional Focus, rail, and navigation state never become legal truth.
 * @authority Python EOS owns status, evidence, identity, and release.
 */
export default function LegalAcceptanceGate({ onComplete, initialPlan = null }) {
  const [plan, setPlan] = useState(initialPlan);
  const [loading, setLoading] = useState(!initialPlan);
  const [submitting, setSubmitting] = useState(null);
  const [error, setError] = useState(null);
  const [confirmationState, setConfirmationState] = useState(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [documentFocusId, setDocumentFocusId] = useState(null);
  const [railCollapsed, setRailCollapsed] = useState(false);
  const [mobileRailOpen, setMobileRailOpen] = useState(false);
  const railBeforeFocus = useRef(false);
  const completionNotified = useRef(false);

  const notifyComplete = useCallback(() => { if (!completionNotified.current) { completionNotified.current = true; onComplete?.(); } }, [onComplete]);
  const loadPlan = useCallback(async ({ showLoading = true } = {}) => {
    if (showLoading) setLoading(true);
    setError(null);
    try {
      const response = await api.get('/legal-acceptance/status');
      const nextPlan = response.data;
      setPlan(nextPlan);
      if (nextPlan?.status === 'COMPLETE') notifyComplete();
      return nextPlan;
    } catch (requestError) {
      setError(diagnosticFor(requestError, 'LEGAL STATUS UNAVAILABLE'));
      return null;
    } finally { if (showLoading) setLoading(false); }
  }, [notifyComplete]);

  useEffect(() => {
    if (initialPlan) { setPlan(initialPlan); setLoading(false); if (initialPlan.status === 'COMPLETE') notifyComplete(); return; }
    loadPlan();
  }, [initialPlan, loadPlan, notifyComplete]);

  const documents = useMemo(() => (Array.isArray(plan?.documents) ? plan.documents : []), [plan?.documents]);
  const recordedCount = documents.filter((document) => document.accepted).length;
  const total = documents.length;
  const remainingCount = Math.max(0, total - recordedCount);
  const selectedDocument = documents.find((document) => document.documentId === selectedDocumentId) || documents.find((document) => !document.accepted) || documents[0] || null;
  const focusDocument = documents.find((document) => document.documentId === documentFocusId) || null;
  const focusIndex = focusDocument ? documents.findIndex((document) => document.documentId === focusDocument.documentId) : -1;

  useEffect(() => { if (selectedDocument && selectedDocument.documentId !== selectedDocumentId) setSelectedDocumentId(selectedDocument.documentId); if (!selectedDocument && selectedDocumentId !== null) setSelectedDocumentId(null); }, [selectedDocument, selectedDocumentId]);

  const toggleRail = () => {
    if (typeof window !== 'undefined' && window.innerWidth < 768) setMobileRailOpen((open) => !open);
    else setRailCollapsed((collapsed) => !collapsed);
  };
  const enterFocus = (documentId) => { railBeforeFocus.current = railCollapsed; setRailCollapsed(true); setMobileRailOpen(false); setSelectedDocumentId(documentId); setDocumentFocusId(documentId); };
  const returnToControl = () => { setDocumentFocusId(null); setRailCollapsed(railBeforeFocus.current); setMobileRailOpen(false); };
  const navigateFocus = (offset) => { if (focusIndex < 0) return; const next = documents[focusIndex + offset]; if (next) { setSelectedDocumentId(next.documentId); setDocumentFocusId(next.documentId); } };

  useEffect(() => {
    if (!focusDocument) return undefined;
    const handleKeyDown = (event) => { const target = event.target; const editing = target instanceof HTMLElement && (target.isContentEditable || ['INPUT', 'SELECT', 'TEXTAREA'].includes(target.tagName)); if (event.key === 'Escape' && !editing && !event.defaultPrevented) { event.preventDefault(); returnToControl(); } };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [focusDocument]);

  const recordEvidence = async (document) => {
    setSubmitting(document.documentId); setError(null); setConfirmationState(null);
    try {
      await api.post('/legal-acceptance/accept', { document_id: document.documentId, document_version: document.version, document_sha3_512: document.sha3_512, acceptance_method: evidenceMethodFor(document), locale: document.locale || 'en-ZA' }, { headers: { 'Idempotency-Key': newIdempotencyKey() } });
      const refreshed = await loadPlan({ showLoading: false });
      const refreshedDocuments = Array.isArray(refreshed?.documents) ? refreshed.documents : [];
      const refreshedDocument = refreshedDocuments.find((item) => item.documentId === document.documentId);
      if (refreshedDocument?.accepted === true) setConfirmationState(null);
      else setConfirmationState({ documentId: document.documentId, status: refreshed ? 'pending' : 'unavailable' });
    } catch (requestError) { setError(diagnosticFor(requestError, 'EVIDENCE RECORDING REJECTED')); }
    finally { setSubmitting(null); }
  };

  if (loading) return <ShellFrame plan={plan} recordedCount={0} total={0} remainingCount={0} railCollapsed={railCollapsed} mobileRailOpen={mobileRailOpen} onToggleRail={toggleRail} onCloseMobileRail={() => setMobileRailOpen(false)}><main className="flex h-full items-center justify-center px-5"><section className="w-full max-w-xl border border-white/[0.09] bg-[#0d100e] p-6"><p className="text-[9px] font-bold uppercase tracking-[0.18em] text-[#b99a45]">LEGAL ADMISSION CONTROL</p><div className="mt-5 flex items-center gap-3"><Loader2 className="h-4 w-4 animate-spin text-[#d4af37]" /><div><h1 className="text-lg font-semibold">Resolving server evidence</h1><p className="mt-1 text-xs text-stone-500">Workspace release remains sealed until the current plan is known.</p></div></div></section></main></ShellFrame>;
  if (error && !plan) return <ShellFrame plan={plan} recordedCount={0} total={0} remainingCount={0} railCollapsed={railCollapsed} mobileRailOpen={mobileRailOpen} onToggleRail={toggleRail} onCloseMobileRail={() => setMobileRailOpen(false)}><main className="flex h-full items-center justify-center px-5"><section role="alert" className="w-full max-w-xl border border-red-400/20 bg-[#110d0d] p-6"><p className="text-[9px] font-bold uppercase tracking-[0.18em] text-red-300">ADMISSION AUTHORITY UNAVAILABLE</p><ErrorSurface error={error} compact /></section></main></ShellFrame>;
  if (!plan) return null;
  const missingAgreementTypes = Array.isArray(plan.missingAgreementTypes) ? plan.missingAgreementTypes : [];
  const emptyPlan = (plan.status === 'USER_TERMS_REQUIRED' || plan.status === 'DOCUMENT_APPROVAL_REQUIRED') && total === 0;
  if (emptyPlan) return <ShellFrame plan={plan} recordedCount={0} total={0} remainingCount={0} railCollapsed={railCollapsed} mobileRailOpen={mobileRailOpen} onToggleRail={toggleRail} onCloseMobileRail={() => setMobileRailOpen(false)}><main className="flex h-full items-center justify-center px-5"><section role="status" className="w-full max-w-2xl border border-[#d4af37]/20 bg-[#0d100e] p-6"><p className="text-[9px] font-bold uppercase tracking-[0.18em] text-[#b99a45]">LEGAL ADMISSION CONTROL · SEALED</p><h1 className="mt-3 text-xl font-semibold">{plan.status === 'USER_TERMS_REQUIRED' ? 'Required documents are not yet available' : 'Legal documents are being prepared'}</h1><p className="mt-2 max-w-xl text-sm leading-6 text-stone-400">Workspace access remains unavailable until the required server documents are published and recorded. This screen does not record evidence.</p>{missingAgreementTypes.length > 0 && <ul aria-label="Missing agreement types" className="mt-5 grid gap-2 sm:grid-cols-2">{missingAgreementTypes.map((item) => <li key={item} className="border border-white/[0.07] px-3 py-2 font-mono text-[10px] text-stone-400">{item}</li>)}</ul>}<p className="mt-6 border-t border-white/[0.07] pt-3 text-[8px] font-bold uppercase tracking-[0.14em] text-stone-700">No inferred evidence · fail closed</p></section></main></ShellFrame>;
  const nextUnresolved = focusIndex >= 0 ? documents.find((item, itemIndex) => itemIndex > focusIndex && !item.accepted) || documents.find((item) => !item.accepted) : null;
  const goToNextUnresolved = () => { if (nextUnresolved) enterFocus(nextUnresolved.documentId); };
  if (focusDocument) return <ShellFrame plan={plan} recordedCount={recordedCount} total={total} remainingCount={remainingCount} railCollapsed={railCollapsed} mobileRailOpen={mobileRailOpen} onToggleRail={toggleRail} onCloseMobileRail={() => setMobileRailOpen(false)} focusMode><DocumentFocusFrame plan={plan} document={focusDocument} documents={documents} index={focusIndex} submitting={submitting} error={error} confirmationState={confirmationState} nextUnresolved={nextUnresolved} onNextUnresolved={goToNextUnresolved} onReturn={returnToControl} onPrevious={() => navigateFocus(-1)} onNext={() => navigateFocus(1)} recordEvidence={recordEvidence} /></ShellFrame>;

  return <ShellFrame plan={plan} recordedCount={recordedCount} total={total} remainingCount={remainingCount} railCollapsed={railCollapsed} mobileRailOpen={mobileRailOpen} onToggleRail={toggleRail} onCloseMobileRail={() => setMobileRailOpen(false)}><main className="flex h-full min-h-0 flex-col overflow-hidden"><header data-testid="control-strip" className="flex min-h-[76px] shrink-0 flex-wrap items-center justify-between gap-3 border-b border-white/[0.08] bg-[#0b0e0c] px-4 py-3 sm:px-6"><div><p className="text-[9px] font-bold uppercase tracking-[0.18em] text-[#b99a45]">LEGAL ADMISSION CONTROL</p><p className="mt-1 text-xs text-stone-500">Operate the server-issued document ledger.</p></div><div className="flex flex-wrap items-center gap-1.5"><Compartment label="REQUIRED" value={total} mono /><Compartment label="RECORDED" value={recordedCount} mono /><Compartment label="REMAINING" value={remainingCount} mono /><Compartment label="WORKSPACE" value="SEALED" /></div></header><div className="grid min-h-0 flex-1 gap-3 overflow-y-auto px-3 py-3 sm:px-5 lg:grid-cols-[minmax(0,1fr)_280px]"><section aria-label="Document ledger" className="min-w-0 border border-white/[0.08] bg-[#0b0e0c]"><div className="flex items-center justify-between border-b border-white/[0.08] px-3 py-2.5"><div><p className="text-[8px] font-bold uppercase tracking-[0.16em] text-stone-600">Controlled records</p><h1 className="mt-1 text-sm font-semibold uppercase tracking-[0.07em] text-stone-200">Document ledger</h1></div><span className="font-mono text-[10px] text-stone-600">{total} rows</span></div><div className="hidden grid-cols-[24px_minmax(0,1.6fr)_minmax(110px,0.7fr)_minmax(110px,0.7fr)_minmax(100px,0.7fr)_auto] gap-3 border-b border-white/[0.07] px-3 py-2 text-[8px] font-bold uppercase tracking-[0.13em] text-stone-600 sm:grid"><span>Focus</span><span>Document</span><span>Type</span><span>Version</span><span>Method</span><span>State</span></div><div role="table" aria-label="Required legal document records" className="divide-y divide-white/[0.07]">{documents.map((document) => { const selected = selectedDocument?.documentId === document.documentId; return <button key={`${document.documentId}:${document.version}`} type="button" role="row" aria-selected={selected} onClick={() => setSelectedDocumentId(document.documentId)} onDoubleClick={() => enterFocus(document.documentId)} className={`group grid w-full grid-cols-[24px_minmax(0,1fr)_auto] items-center gap-2 border-l-2 px-3 py-2.5 text-left transition motion-reduce:transition-none sm:grid-cols-[24px_minmax(0,1.6fr)_minmax(110px,0.7fr)_minmax(110px,0.7fr)_minmax(100px,0.7fr)_auto] sm:gap-3 ${selected ? 'border-l-[#d4af37] bg-[#d4af37]/[0.07]' : 'border-l-transparent bg-[#0b0e0c] hover:bg-white/[0.025]'}`}><span className={`h-2 w-2 rounded-full border ${selected ? 'border-[#f0d477] bg-[#d4af37]' : document.accepted ? 'border-emerald-300 bg-emerald-300' : 'border-[#b99a45]'}`} aria-label={selected ? 'Focused row' : 'Record'} /><span className="min-w-0"><span className="block truncate text-xs font-semibold text-stone-100">{document.title}</span><span className="mt-0.5 block truncate font-mono text-[9px] uppercase tracking-[0.06em] text-stone-600 sm:hidden">{recordTypeFor(document)} · v{document.version} · {evidenceMethodFor(document)}</span></span><span className="hidden truncate font-mono text-[9px] uppercase text-stone-500 sm:block">{recordTypeFor(document)}</span><span className="hidden font-mono text-[10px] text-stone-500 sm:block">v{document.version}</span><span className="hidden text-[9px] font-bold uppercase text-[#b99a45] sm:block">{evidenceMethodFor(document)}</span><span className={`truncate text-[9px] font-bold uppercase ${document.accepted ? 'text-emerald-300' : isIntegrityBlocked(document) ? 'text-amber-200' : 'text-stone-500'}`}>{isIntegrityBlocked(document) ? 'REVIEW' : document.accepted ? 'RECORDED' : 'REQUIRED'}<ChevronRight className="ml-1 inline h-3 w-3 text-stone-700" aria-hidden="true" /></span></button>; })}</div></section><aside aria-label="Selected legal record" className="h-fit min-w-0 border border-white/[0.08] bg-[#0b0e0c] p-4"><p className="text-[8px] font-bold uppercase tracking-[0.16em] text-[#b99a45]">Selected record</p>{selectedDocument ? <><h2 className="mt-2 text-sm font-semibold leading-5 text-stone-100">{selectedDocument.title}</h2><dl className="mt-4 grid grid-cols-2 gap-2 text-[9px]"><div><dt className="text-stone-600">TYPE</dt><dd className="mt-1 font-mono uppercase text-stone-400">{recordTypeFor(selectedDocument)}</dd></div><div><dt className="text-stone-600">VERSION</dt><dd className="mt-1 font-mono text-stone-400">{selectedDocument.version}</dd></div><div><dt className="text-stone-600">METHOD</dt><dd className="mt-1 font-bold uppercase text-[#b99a45]">{evidenceMethodFor(selectedDocument)}</dd></div><div><dt className="text-stone-600">STATE</dt><dd className="mt-1 font-bold uppercase text-stone-400">{isIntegrityBlocked(selectedDocument) ? 'REVIEW' : selectedDocument.accepted ? 'RECORDED' : 'REQUIRED'}</dd></div></dl>{isIntegrityBlocked(selectedDocument) && <div role="alert" className="mt-4 border border-amber-300/25 bg-amber-300/[0.045] px-3 py-2 text-[10px] leading-4 text-amber-100">Integrity review required before evidence can be recorded.</div>}<button type="button" onClick={() => enterFocus(selectedDocument.documentId)} className="mt-5 flex min-h-10 w-full items-center justify-center gap-2 border border-white/[0.16] px-3 text-[10px] font-bold uppercase tracking-[0.1em] text-stone-300 transition hover:border-[#d4af37]/60 hover:text-[#f0d477] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d4af37]">Review document <ChevronRight className="h-3.5 w-3.5" /></button></> : <p className="mt-3 text-xs text-stone-500">No server-issued record is available.</p>}</aside>{error && <ErrorSurface error={error} compact />}</div></main></ShellFrame>;
}

// ARTIFACT: LegalAcceptanceGate.jsx
// VERSION: v1.8.0-RECORD-NAVIGATION-SCROLL-RESET
// AUTHORITY BOUNDARY: client projection only; no signature or commercial execution
// TENANT POSTURE: server-issued acceptance plan only; no localStorage legal truth
// FAIL-CLOSED POSTURE: unavailable, incomplete, or integrity-blocked plans never enter workspace
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
