import React, { useCallback, useEffect, useState } from 'react';
import api from '../../services/api';

const VERIFICATION_CHECKS = [
  ['RATIFIER_AUTHORITY', 'Ratifier authority independently verified'],
  ['CONTRACT_VERSION_AND_FINGERPRINT', 'Canonical contract version and fingerprint verified'],
  ['DECISION_REGISTER_COMPLETENESS', 'D01-D10 decision register completeness verified'],
  ['DECISION_EVIDENCE_AND_SCOPE', 'Decision evidence and explicit scope verified'],
  ['EFFECTIVE_REVIEW_AND_REVOCATION', 'Effective time, review time, and revocation controls verified'],
  ['INSTITUTION_BINDING', 'Institution binding independently verified'],
  ['TENANT_BINDING', 'Authenticated tenant binding independently verified'],
  ['SECOND_APPROVAL_POLICY', 'Second-approval policy source independently verified'],
];

const FINGERPRINT = /^[0-9a-f]{128}$/;

export default function G64ReviewWorkflow({ institutionId, recordId, recordFingerprint }) {
  const [selectedRecord, setSelectedRecord] = useState(recordId || '');
  const [fingerprint, setFingerprint] = useState(recordFingerprint || '');
  const [evidenceLocator, setEvidenceLocator] = useState('');
  const [evidenceFingerprint, setEvidenceFingerprint] = useState('');
  const [rationale, setRationale] = useState('');
  const [verificationChecks, setVerificationChecks] = useState(() => VERIFICATION_CHECKS.map(([check]) => ({
    check, passed: false, rationale: '',
  })));
  const [verificationOutcome, setVerificationOutcome] = useState('FAIL');
  const [verificationEvents, setVerificationEvents] = useState([]);
  const [approvalOutcome, setApprovalOutcome] = useState('REJECT');
  const [approvalRationale, setApprovalRationale] = useState('');
  const [approvalEvidenceLocator, setApprovalEvidenceLocator] = useState('');
  const [approvalEvidenceFingerprint, setApprovalEvidenceFingerprint] = useState('');
  const [selectedVerification, setSelectedVerification] = useState('');
  const [secondApprovalRequired, setSecondApprovalRequired] = useState('UNDECIDED');
  const [policyRationale, setPolicyRationale] = useState('');
  const [policySourceLocator, setPolicySourceLocator] = useState('');
  const [policySourceFingerprint, setPolicySourceFingerprint] = useState('');
  const [policyVerificationLocator, setPolicyVerificationLocator] = useState('');
  const [policyVerificationFingerprint, setPolicyVerificationFingerprint] = useState('');
  const [selectedPolicyEvent, setSelectedPolicyEvent] = useState('');
  const [policyIdempotencyKey, setPolicyIdempotencyKey] = useState('');
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [verificationIdempotencyKey, setVerificationIdempotencyKey] = useState('');
  const [approvalIdempotencyKey, setApprovalIdempotencyKey] = useState('');

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
      const key = verificationIdempotencyKey || `g64-verification-${window.crypto?.randomUUID?.() || Date.now().toString(36)}`;
      setVerificationIdempotencyKey(key);
      const { data } = await api.post(
        `/legal-operations/g64/ratification-workspace/records/${encodeURIComponent(selectedRecord)}/independent-verification`,
        {
          institution_id: institutionId,
          record_id: selectedRecord,
          record_sha3_512_fingerprint: fingerprint,
          outcome: verificationOutcome,
          rationale,
          findings: verificationChecks.map((item) => ({
            check: item.check,
            passed: item.passed,
            rationale: item.rationale.trim() || rationale.trim(),
            evidence: [{ locator: evidenceLocator, sha3_512_fingerprint: evidenceFingerprint }],
          })),
        },
        { headers: { 'Idempotency-Key': key } }
      );
      setVerificationIdempotencyKey('');
      setStatusText(`Verification event saved: ${data.review_event.event_id}. This is an evidence attestation, not external certification.`);
      await refreshEvents();
    } catch (cause) {
      setError(cause?.response?.data?.detail || 'Independent verification was not confirmed by Python EOS.');
    } finally {
      setBusy(false);
    }
  };

  const submitPolicy = async (event) => {
    event.preventDefault();
    if (secondApprovalRequired === 'UNDECIDED') {
      setError('Determine the second-approval requirement from an authoritative policy source.');
      return;
    }
    setBusy(true);
    setError('');
    setStatusText('');
    try {
      const key = policyIdempotencyKey || `g64-policy-${window.crypto?.randomUUID?.() || Date.now().toString(36)}`;
      setPolicyIdempotencyKey(key);
      const { data } = await api.post(
        `/legal-operations/g64/ratification-workspace/records/${encodeURIComponent(selectedRecord)}/second-approval-policy`,
        {
          institution_id: institutionId,
          record_id: selectedRecord,
          record_sha3_512_fingerprint: fingerprint,
          verification_event_id: selectedVerification,
          second_approval_required: secondApprovalRequired === 'REQUIRED',
          rationale: policyRationale,
          policy_source: { locator: policySourceLocator, sha3_512_fingerprint: policySourceFingerprint },
          independent_verification_evidence: { locator: policyVerificationLocator, sha3_512_fingerprint: policyVerificationFingerprint },
        },
        { headers: { 'Idempotency-Key': key } }
      );
      setPolicyIdempotencyKey('');
      setSelectedPolicyEvent(data.review_event.event_id);
      setStatusText(`Policy determination saved: ${data.review_event.event_id}. It does not authorize access.`);
      await refreshEvents();
    } catch (cause) {
      setError(cause?.response?.data?.detail || 'Second-approval policy determination was not confirmed by Python EOS.');
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
      const key = approvalIdempotencyKey || `g64-second-approval-${window.crypto?.randomUUID?.() || Date.now().toString(36)}`;
      setApprovalIdempotencyKey(key);
      const { data } = await api.post(
        `/legal-operations/g64/ratification-workspace/records/${encodeURIComponent(selectedRecord)}/second-approval`,
        {
          institution_id: institutionId,
          record_id: selectedRecord,
          record_sha3_512_fingerprint: fingerprint,
          verification_event_id: selectedVerification,
          policy_decision_event_id: selectedPolicyEvent,
          outcome: approvalOutcome,
          rationale: approvalRationale,
          evidence: [{ locator: approvalEvidenceLocator, sha3_512_fingerprint: approvalEvidenceFingerprint }],
        },
        { headers: { 'Idempotency-Key': key } }
      );
      setApprovalIdempotencyKey('');
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
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Complete all eight verification checks</h4>
          {verificationChecks.map((item, index) => (
            <div key={item.check} className="space-y-2 rounded-md border border-slate-700 p-3">
              <label className="flex gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={item.passed}
                  onChange={(event) => setVerificationChecks((current) => current.map((check, position) => position === index ? { ...check, passed: event.target.checked } : check))}
                />
                {VERIFICATION_CHECKS[index][1]}
              </label>
              <input
                value={item.rationale}
                onChange={(event) => setVerificationChecks((current) => current.map((check, position) => position === index ? { ...check, rationale: event.target.value } : check))}
                minLength={20}
                maxLength={2000}
                required
                placeholder="Rationale for this specific check"
                className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm"
              />
            </div>
          ))}
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
        <button type="submit" disabled={!valid || rationale.trim().length < 20 || verificationChecks.some((item) => item.rationale.trim().length < 20) || (verificationOutcome === 'PASS' && verificationChecks.some((item) => !item.passed)) || (verificationOutcome === 'FAIL' && verificationChecks.every((item) => item.passed)) || busy} className="rounded-lg bg-violet-300 px-4 py-2 font-semibold text-slate-950 disabled:opacity-40">
          Save independent verification evidence
        </button>
      </form>

      <form onSubmit={submitPolicy} className="space-y-3 rounded-lg border border-slate-700 p-3">
        <h3 className="font-semibold">Determine whether second approval is mandatory</h3>
        <p className="text-xs leading-5 text-slate-400">Do not guess. Use the governing policy source and a distinct independent verification reference. This decision is evidence only.</p>
        <label className="block text-sm">Policy determination
          <select value={secondApprovalRequired} onChange={(event) => setSecondApprovalRequired(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2">
            <option value="UNDECIDED">Undecided</option>
            <option value="REQUIRED">Second approval required</option>
            <option value="NOT_REQUIRED">Second approval not required by policy</option>
          </select>
        </label>
        <label className="block text-sm">Policy rationale
          <textarea value={policyRationale} onChange={(event) => setPolicyRationale(event.target.value)} minLength={20} maxLength={4000} required rows={2} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2" />
        </label>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="block text-sm">Authoritative policy locator
            <input value={policySourceLocator} onChange={(event) => setPolicySourceLocator(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2" />
          </label>
          <label className="block text-sm">Policy SHA3-512
            <input value={policySourceFingerprint} onChange={(event) => setPolicySourceFingerprint(event.target.value.trim().toLowerCase())} required minLength={128} maxLength={128} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 font-mono text-xs" />
          </label>
          <label className="block text-sm">Independent verification evidence locator
            <input value={policyVerificationLocator} onChange={(event) => setPolicyVerificationLocator(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2" />
          </label>
          <label className="block text-sm">Independent verification evidence SHA3-512
            <input value={policyVerificationFingerprint} onChange={(event) => setPolicyVerificationFingerprint(event.target.value.trim().toLowerCase())} required minLength={128} maxLength={128} className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 font-mono text-xs" />
          </label>
        </div>
        <button type="submit" disabled={!valid || !selectedVerification || secondApprovalRequired === 'UNDECIDED' || policyRationale.trim().length < 20 || !policySourceLocator.trim() || !FINGERPRINT.test(policySourceFingerprint.trim().toLowerCase()) || !policyVerificationLocator.trim() || !FINGERPRINT.test(policyVerificationFingerprint.trim().toLowerCase()) || busy} className="rounded-lg border border-cyan-300 px-4 py-2 font-semibold disabled:opacity-40">
          Save second-approval policy evidence
        </button>
      </form>

      <form onSubmit={submitApproval} className="space-y-3 rounded-lg border border-slate-700 p-3">
        <h3 className="font-semibold">Second approval (only when policy requires it)</h3>
        <label className="block text-sm">Evidence-backed policy decision
          <select value={selectedPolicyEvent} onChange={(event) => setSelectedPolicyEvent(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2">
            <option value="">Choose a policy decision requiring approval</option>
            {verificationEvents.filter((item) => item.event_type === 'SECOND_APPROVAL_POLICY' && item.second_approval_required === true).map((item) => <option key={item.event_id} value={item.event_id}>{item.event_id}</option>)}
          </select>
        </label>
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
        <button type="submit" disabled={!valid || !selectedVerification || !selectedPolicyEvent || approvalRationale.trim().length < 20 || !approvalEvidenceLocator.trim() || !FINGERPRINT.test(approvalEvidenceFingerprint.trim().toLowerCase()) || busy} className="rounded-lg border border-violet-300 px-4 py-2 font-semibold disabled:opacity-40">
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
          <p className="mt-1 text-slate-400">Actor: {item.verifier_principal_id || item.reviewer_principal_id || item.determined_by_principal_id || item.approver_principal_id}</p>
        </li>
      ))}</ul>}
    </section>
  );
}
