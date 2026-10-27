import React, { useCallback, useEffect, useState } from 'react';
import api from '../../services/api';

const FINGERPRINT = /^[0-9a-f]{128}$/;

export default function G64ReviewWorkflow({ institutionId, recordId, recordFingerprint }) {
  const [selectedRecord, setSelectedRecord] = useState(recordId || '');
  const [fingerprint, setFingerprint] = useState(recordFingerprint || '');
  const [evidenceLocator, setEvidenceLocator] = useState('');
  const [evidenceFingerprint, setEvidenceFingerprint] = useState('');
  const [rationale, setRationale] = useState('');
  const [bindingVerified, setBindingVerified] = useState(false);
  const [authorityVerified, setAuthorityVerified] = useState(false);
  const [integrityVerified, setIntegrityVerified] = useState(false);
  const [verificationOutcome, setVerificationOutcome] = useState('FAIL');
  const [verificationEvents, setVerificationEvents] = useState([]);
  const [approvalOutcome, setApprovalOutcome] = useState('REJECT');
  const [approvalRationale, setApprovalRationale] = useState('');
  const [approvalEvidenceLocator, setApprovalEvidenceLocator] = useState('');
  const [approvalEvidenceFingerprint, setApprovalEvidenceFingerprint] = useState('');
  const [selectedVerification, setSelectedVerification] = useState('');
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (recordId) setSelectedRecord(recordId);
    if (recordFingerprint) setFingerprint(recordFingerprint);
  }, [recordId, recordFingerprint]);

  const refreshEvents = useCallback(async () => {
    if (!institutionId || !selectedRecord) return;
    try {
      const { data } = await api.get(
        `/legal-operations/g64/ratification-workspace/records/${encodeURIComponent(selectedRecord)}/review-events`,
        { params: { institution_id: institutionId, limit: 100 } }
      );
      const events = data.review_events || [];
      setVerificationEvents(events);
      if (!selectedVerification) {
        const passing = events.find((event) => event.event_type === 'INDEPENDENT_VERIFICATION' && event.outcome === 'PASS');
        if (passing) setSelectedVerification(passing.event_id);
      }
    } catch (cause) {
      setError(cause?.response?.data?.detail || 'Review evidence is unavailable.');
    }
  }, [institutionId, selectedRecord, selectedVerification]);

  useEffect(() => { refreshEvents(); }, [refreshEvents]);

  const submitVerification = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    setStatusText('');
    try {
      const { data } = await api.post(
        `/legal-operations/g64/ratification-workspace/records/${encodeURIComponent(selectedRecord)}/independent-verification`,
        {
          institution_id: institutionId,
          record_id: selectedRecord,
          record_sha3_512_fingerprint: fingerprint,
          outcome: verificationOutcome,
          institution_binding_verified: bindingVerified,
          ratifier_authority_verified: authorityVerified,
          evidence_integrity_verified: integrityVerified,
          rationale,
          evidence: [{ locator: evidenceLocator, sha3_512_fingerprint: evidenceFingerprint }],
        },
        { headers: { 'Idempotency-Key': `g64-verification-${window.crypto?.randomUUID?.() || Date.now().toString(36)}` } }
      );
      setStatusText(`Verification event saved: ${data.review_event.event_id}. This is an evidence attestation, not external certification.`);
      await refreshEvents();
    } catch (cause) {
      setError(cause?.response?.data?.detail || 'Independent verification was not confirmed by Python EOS.');
    } finally {
      setBusy(false);
    }
  };

  const submitApproval = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    setStatusText('');
    try {
      const { data } = await api.post(
        `/legal-operations/g64/ratification-workspace/records/${encodeURIComponent(selectedRecord)}/second-approval`,
        {
          institution_id: institutionId,
          record_id: selectedRecord,
          record_sha3_512_fingerprint: fingerprint,
          verification_event_id: selectedVerification,
          outcome: approvalOutcome,
          rationale: approvalRationale,
          evidence: [{ locator: approvalEvidenceLocator, sha3_512_fingerprint: approvalEvidenceFingerprint }],
        },
        { headers: { 'Idempotency-Key': `g64-second-approval-${window.crypto?.randomUUID?.() || Date.now().toString(36)}` } }
      );
      setStatusText(`Second-approval event saved: ${data.review_event.event_id}. Ratification remains incomplete.`);
      await refreshEvents();
    } catch (cause) {
      setError(cause?.response?.data?.detail || 'Second approval was not confirmed by Python EOS.');
    } finally {
      setBusy(false);
    }
  };

  const valid = Boolean(
    institutionId && selectedRecord && FINGERPRINT.test(fingerprint) &&
    evidenceLocator.trim() && FINGERPRINT.test(evidenceFingerprint.trim().toLowerCase())
  );
  const passingVerifications = verificationEvents.filter(
    (item) => item.event_type === 'INDEPENDENT_VERIFICATION' && item.outcome === 'PASS'
  );

  return (
    <section className="space-y-5 rounded-xl border border-violet-700/50 bg-slate-900 p-4">
      <header>
        <h2 className="text-xl font-semibold">Independent verification and second approval</h2>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          Use separate authenticated principals for ratification attestation, independent verification,
          and second approval. Submitted findings are durable review evidence only; they do not
          independently prove the truth of source documents, grant authority, or activate access.
        </p>
      </header>

      <div className="grid gap-3 md:grid-cols-2">
        <label className="space-y-1 text-sm">
          <span className="block">Workspace record ID</span>
          <input value={selectedRecord} onChange={(event) => setSelectedRecord(event.target.value)} required className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 font-mono text-xs" />
        </label>
        <label className="space-y-1 text-sm">
          <span className="block">Workspace SHA3-512 fingerprint</span>
          <input value={fingerprint} onChange={(event) => setFingerprint(event.target.value.trim().toLowerCase())} required minLength={128} maxLength={128} className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 font-mono text-xs" />
        </label>
      </div>

      <form onSubmit={submitVerification} className="space-y-3 rounded-lg border border-slate-700 p-3">
        <h3 className="font-semibold">Independent verification finding</h3>
        <label className="block text-sm">Outcome
          <select value={verificationOutcome} onChange={(event) => setVerificationOutcome(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2">
            <option value="FAIL">FAIL / deny</option>
            <option value="PASS">PASS / all checks independently confirmed</option>
          </select>
        </label>
        <div className="space-y-2 text-sm">
          <label className="flex gap-2"><input type="checkbox" checked={bindingVerified} onChange={(event) => setBindingVerified(event.target.checked)} /> Institution binding independently verified</label>
          <label className="flex gap-2"><input type="checkbox" checked={authorityVerified} onChange={(event) => setAuthorityVerified(event.target.checked)} /> Ratifier authority independently verified</label>
          <label className="flex gap-2"><input type="checkbox" checked={integrityVerified} onChange={(event) => setIntegrityVerified(event.target.checked)} /> Source evidence integrity independently verified</label>
        </div>
        <label className="block text-sm">Verification rationale
          <textarea value={rationale} onChange={(event) => setRationale(event.target.value)} minLength={20} maxLength={4000} required rows={3} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2" />
        </label>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="block text-sm">Evidence locator
            <input value={evidenceLocator} onChange={(event) => setEvidenceLocator(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2" />
          </label>
          <label className="block text-sm">Evidence SHA3-512
            <input value={evidenceFingerprint} onChange={(event) => setEvidenceFingerprint(event.target.value.trim().toLowerCase())} required minLength={128} maxLength={128} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 font-mono text-xs" />
          </label>
        </div>
        <button type="submit" disabled={!valid || rationale.trim().length < 20 || busy} className="rounded-lg bg-violet-300 px-4 py-2 font-semibold text-slate-950 disabled:opacity-40">
          Save independent verification evidence
        </button>
      </form>

      <form onSubmit={submitApproval} className="space-y-3 rounded-lg border border-slate-700 p-3">
        <h3 className="font-semibold">Mandatory second approval</h3>
        <label className="block text-sm">Prior PASS verification event
          <select value={selectedVerification} onChange={(event) => setSelectedVerification(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2">
            <option value="">Choose verified event</option>
            {passingVerifications.map((item) => <option key={item.event_id} value={item.event_id}>{item.event_id}</option>)}
          </select>
        </label>
        <label className="block text-sm">Outcome
          <select value={approvalOutcome} onChange={(event) => setApprovalOutcome(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2">
            <option value="REJECT">REJECT / deny</option>
            <option value="APPROVE">APPROVE second review</option>
          </select>
        </label>
        <label className="block text-sm">Second-approval rationale
          <textarea value={approvalRationale} onChange={(event) => setApprovalRationale(event.target.value)} minLength={20} maxLength={4000} required rows={3} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2" />
        </label>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="block text-sm">Approval evidence locator
            <input value={approvalEvidenceLocator} onChange={(event) => setApprovalEvidenceLocator(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2" />
          </label>
          <label className="block text-sm">Approval evidence SHA3-512
            <input value={approvalEvidenceFingerprint} onChange={(event) => setApprovalEvidenceFingerprint(event.target.value.trim().toLowerCase())} required minLength={128} maxLength={128} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 font-mono text-xs" />
          </label>
        </div>
        <button type="submit" disabled={!valid || !selectedVerification || approvalRationale.trim().length < 20 || !approvalEvidenceLocator.trim() || !FINGERPRINT.test(approvalEvidenceFingerprint.trim().toLowerCase()) || busy} className="rounded-lg border border-violet-300 px-4 py-2 font-semibold disabled:opacity-40">
          Save second-approval evidence
        </button>
      </form>

      <div className="flex items-center gap-3">
        <button type="button" onClick={refreshEvents} disabled={!selectedRecord || busy} className="rounded-lg border border-slate-600 px-3 py-2 text-sm disabled:opacity-40">Refresh review history</button>
        <span className="text-xs text-slate-400">{verificationEvents.length} persisted review events</span>
      </div>
      {error && <p role="alert" className="rounded-lg border border-red-500/50 p-3 text-sm text-red-200">{error}</p>}
      {statusText && <p role="status" className="rounded-lg border border-emerald-700/50 p-3 text-sm text-emerald-100">{statusText}</p>}
      <p className="text-sm text-amber-200">Ratification complete: NO. Operational access enabled: NO.</p>
      {verificationEvents.length > 0 && <ul className="space-y-2">{verificationEvents.map((item) => (
        <li key={item.event_id} className="break-all rounded-lg border border-slate-700 p-3 text-xs">
          <strong>{item.event_type}</strong> · {item.outcome} · {item.event_id}
          <p className="mt-1 text-slate-400">Actor: {item.reviewer_principal_id || item.approver_principal_id}</p>
        </li>
      ))}</ul>}
    </section>
  );
}
