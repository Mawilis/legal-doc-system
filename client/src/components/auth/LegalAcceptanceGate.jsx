/**
 * WILSY OS — VERSIONED LEGAL ACCEPTANCE GATE
 * VERSION: v1.0.2-R1D-B0F-B4-R9A-P3-EMPTY-STATE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Presents the server-issued legal acceptance plan and records only
 *           bounded acknowledgement/acceptance evidence; it never signs contracts.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/auth/LegalAcceptanceGate.jsx
 * COLLABORATION / OWNERSHIP: Python legal_acceptance_router/service own all legal
 *                            truth; this component is a responsive projection.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.0.2 adds an explicit fail-closed presentation for a server
 *            USER_TERMS_REQUIRED plan with no renderable documents while
 *            preserving server authority and the existing acceptance flow.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * TENANT BOUNDARY: Displays only the authenticated server-issued plan.
 * AUTHORITY BOUNDARY: Client presentation only; no legal or commercial execution.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, FileText, Loader2, ShieldCheck } from 'lucide-react';
import api from '@/services/api';

const newIdempotencyKey = () => (
  typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `legal-${Date.now()}-${Math.random().toString(16).slice(2)}`
);

/**
 * @description Render and complete the server-derived acceptance plan.
 * @collaboration Consumes GET/POST /api/legal-acceptance and notifies App routing.
 * @institutional Keeps acknowledgement distinct from organisation-binding contracts.
 */
export default function LegalAcceptanceGate({ onComplete, initialPlan = null }) {
  const [plan, setPlan] = useState(initialPlan);
  const [loading, setLoading] = useState(!initialPlan);
  const [submitting, setSubmitting] = useState(null);
  const [error, setError] = useState(null);

  const loadPlan = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/legal-acceptance/status');
      const nextPlan = response.data;
      setPlan(nextPlan);
      if (nextPlan.status === 'COMPLETE') onComplete?.();
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || requestError.message || 'Legal acceptance is temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  }, [onComplete]);

  useEffect(() => { if (!initialPlan) loadPlan(); }, [initialPlan, loadPlan]);

  const accept = async (document) => {
    setSubmitting(document.documentId);
    setError(null);
    try {
      await api.post('/legal-acceptance/accept', {
        document_id: document.documentId,
        document_version: document.version,
        document_sha3_512: document.sha3_512,
        acceptance_method: document.agreementType === 'INSTITUTIONAL_CHARTER' ? 'ACKNOWLEDGEMENT' : 'ACCEPTANCE',
        locale: document.locale || 'en-ZA',
      }, { headers: { 'Idempotency-Key': newIdempotencyKey() } });
      await loadPlan();
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || requestError.message || 'Acceptance could not be recorded.');
    } finally {
      setSubmitting(null);
    }
  };

  if (loading) return <div className="flex min-h-screen items-center justify-center bg-[#0b0d0c] text-[#d4af37]"><Loader2 className="mr-3 animate-spin" />Loading institutional requirements…</div>;
  if (error && !plan) return <div className="flex min-h-screen items-center justify-center bg-[#0b0d0c] px-6 text-center text-red-300"><AlertTriangle className="mr-3" />{error}</div>;
  if (!plan) return null;
  const documents = Array.isArray(plan.documents) ? plan.documents : [];
  const missingAgreementTypes = Array.isArray(plan.missingAgreementTypes) ? plan.missingAgreementTypes : [];
  const emptyRequiredPlan = plan.status === 'USER_TERMS_REQUIRED' && documents.length === 0;
  const emptyApprovalPlan = plan.status === 'DOCUMENT_APPROVAL_REQUIRED' && documents.length === 0;
  if (emptyRequiredPlan || emptyApprovalPlan) {
    const heading = emptyRequiredPlan
      ? 'Required institutional documents are not yet approved and available'
      : 'Legal documents are being prepared';
    const message = emptyRequiredPlan
      ? 'Workspace access will remain unavailable until the required documents are published and accepted. Seeing this screen does not record an acceptance.'
      : 'Institutional documents are awaiting approval. Workspace access remains protected until an approved document set is available. No legacy covenant or signature is accepted as a substitute.';
    return <div className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center bg-[#0b0d0c] px-6 text-center text-stone-100" role="status" aria-live="polite"><ShieldCheck className="mb-4 h-12 w-12 text-[#d4af37]" /><h1 className="text-2xl font-semibold">{heading}</h1><p className="mt-3 max-w-xl text-sm text-stone-400">{message}</p>{missingAgreementTypes.length > 0 && <div className="mt-5 max-w-xl text-left text-sm text-stone-400"><p className="font-medium text-stone-300">Required document families currently unavailable:</p><ul aria-label="Missing agreement types" className="mt-2 list-disc space-y-1 pl-5">{missingAgreementTypes.map((agreementType) => <li key={agreementType}>{agreementType}</li>)}</ul></div>}{error && <p className="mt-4 text-xs text-red-300">{error}</p>}</div>;
  }
  return (
    <main className="min-h-screen overflow-y-auto bg-[#0b0d0c] px-4 py-8 text-stone-100 sm:px-8">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8 border-b border-stone-800 pb-6">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[#d4af37]">WILSY OS · {plan.tenantId}</p>
          <h1 className="mt-3 text-3xl font-semibold">Before you enter your workspace</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-stone-400">Please review the current institutional documents. WILSY OS uses authorised institutional records as truth; AI assistance does not itself create authority, and consequential actions may require additional approval.</p>
        </header>
        <section className="mb-8 rounded-lg border border-[#d4af37]/30 bg-[#161914] p-5" aria-label="Acceptance principles">
          <div className="flex items-start gap-3"><ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-[#d4af37]" /><p className="text-sm leading-6 text-stone-300">This acknowledgement is attributable to your authenticated identity only. It does not bind your organisation, execute an MSA, accept commercial pricing, or grant signatory authority.</p></div>
        </section>
        <div className="space-y-4">
          {documents.map((document) => <article key={`${document.documentId}:${document.version}`} className="rounded-lg border border-stone-800 bg-[#111411] p-5"><div className="flex flex-wrap items-start justify-between gap-4"><div className="flex gap-3"><FileText className="mt-1 h-5 w-5 shrink-0 text-[#d4af37]" /><div><h2 className="font-medium">{document.title}</h2><p className="mt-1 text-xs text-stone-500">{document.agreementType} · version {document.version} · effective {new Date(document.effectiveFrom).toLocaleDateString()}</p></div></div>{document.accepted ? <span className="inline-flex items-center gap-1 text-xs text-emerald-300"><CheckCircle2 className="h-4 w-4" />Recorded</span> : <button type="button" onClick={() => accept(document)} disabled={submitting === document.documentId} className="rounded-md bg-[#d4af37] px-4 py-2 text-xs font-semibold text-black disabled:opacity-50">{submitting === document.documentId ? 'Recording…' : 'Acknowledge and continue'}</button>}</div><p className="mt-4 text-sm leading-6 text-stone-300">{document.summary}</p><details className="mt-3"><summary className="cursor-pointer text-xs text-[#d4af37]">View full document</summary><div className="mt-3 max-h-64 overflow-y-auto whitespace-pre-wrap border-t border-stone-800 pt-3 text-sm leading-6 text-stone-400">{document.content}</div></details></article>)}
        </div>
        {error && <p role="alert" className="mt-6 flex items-center gap-2 text-sm text-red-300"><AlertTriangle className="h-4 w-4" />{error}</p>}
        <footer className="mt-8 border-t border-stone-800 pt-5 text-xs leading-5 text-stone-500">Act only within your granted institutional authority. The server records the document version, digest, authenticated principal, tenant, session reference, and acceptance fingerprint.</footer>
      </div>
    </main>
  );
}

// ARTIFACT: LegalAcceptanceGate.jsx
// VERSION: v1.0.2-R1D-B0F-B4-R9A-P3-EMPTY-STATE
// AUTHORITY BOUNDARY: client projection only; no signature or commercial execution
// TENANT POSTURE: server-issued acceptance plan only; no localStorage legal truth
// FAIL-CLOSED POSTURE: unavailable or incomplete plan never enters workspace
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
