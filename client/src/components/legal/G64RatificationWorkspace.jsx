import React, { useCallback, useEffect, useMemo, useState } from 'react';
import api from '../../services/api';
import G64ReviewWorkflow from './G64ReviewWorkflow.jsx';

const DECISIONS = [
  ['D01', 'Reviewer eligibility and granting authorization role'],
  ['D02', 'Reviewer target and administrator separation of duties'],
  ['D03', 'Independent no-wall-required authority'],
  ['D04', 'Authoritative wall policy and membership source'],
  ['D05', 'Acknowledgement provenance and effective enforcement'],
  ['D06', 'Emergency denial, revocation and incident authority'],
  ['D07', 'Maximum approval duration and review cadence'],
  ['D08', 'Explicit deny precedence'],
  ['D09', 'Content-read revalidation and transaction boundaries'],
  ['D10', 'Independent policy approval, rollout and rollback ownership'],
];

const blankDecision = ([decisionId, decisionName]) => ({
  decisionId,
  decisionName,
  disposition: '',
  rationale: '',
  scope: '',
  accountableSourceOwner: '',
  evidenceLocator: '',
  evidenceFingerprint: '',
  effectiveFrom: '',
  reviewAt: '',
  revocationRule: '',
});

const FINGERPRINT = /^[0-9a-f]{128}$/;

function toUtc(value) {
  return new Date(value).toISOString();
}

function decisionComplete(item) {
  return Boolean(
    item.disposition &&
    item.rationale.trim() &&
    item.scope.split(',').some((value) => value.trim()) &&
    item.accountableSourceOwner.trim() &&
    item.evidenceLocator.trim() &&
    FINGERPRINT.test(item.evidenceFingerprint.trim()) &&
    item.effectiveFrom &&
    item.reviewAt &&
    Date.parse(item.reviewAt) > Date.parse(item.effectiveFrom) &&
    item.revocationRule.trim()
  );
}

export default function G64RatificationWorkspace() {
  const [contract, setContract] = useState(null);
  const [contractError, setContractError] = useState('');
  const [institutionId, setInstitutionId] = useState('');
  const [decisions, setDecisions] = useState(() => DECISIONS.map(blankDecision));
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyError, setHistoryError] = useState('');
  const [idempotencyKey, setIdempotencyKey] = useState('');

  useEffect(() => {
    let active = true;
    api.get('/legal-operations/g64/ratification-workspace/contract')
      .then(({ data }) => {
        if (active) setContract(data);
      })
      .catch((cause) => {
        if (!active) return;
        setContractError(
          cause?.response?.data?.detail ||
          'The canonical G62 contract could not be loaded from Python EOS.'
        );
      });
    return () => {
      active = false;
    };
  }, []);

  const completeCount = useMemo(
    () => decisions.filter(decisionComplete).length,
    [decisions]
  );
  const canSubmit = Boolean(
    contract &&
    institutionId.trim() &&
    completeCount === DECISIONS.length &&
    confirmed &&
    !busy
  );

  const updateDecision = useCallback((decisionId, field, value) => {
    setDecisions((current) => current.map((item) => (
      item.decisionId === decisionId ? { ...item, [field]: value } : item
    )));
    setResult(null);
    setError('');
    setIdempotencyKey('');
  }, []);

  const loadHistory = useCallback(async () => {
    if (!institutionId.trim()) {
      setHistoryError('Enter the institution identifier label before requesting saved evidence.');
      return;
    }
    setHistoryError('');
    try {
      const { data } = await api.get(
        '/legal-operations/g64/ratification-workspace/records',
        { params: { institution_id: institutionId.trim(), limit: 50 } }
      );
      setHistory(data.records || []);
    } catch (cause) {
      setHistoryError(
        cause?.response?.data?.detail ||
        'Saved evidence history is unavailable; no browser-side authority is inferred.'
      );
    }
  }, [institutionId]);

  const submitAttestation = async (event) => {
    event.preventDefault();
    setError('');
    setResult(null);
    if (!canSubmit) {
      setError('Choose and complete every D01–D10 disposition and confirm the attestation statement.');
      return;
    }
    const key = idempotencyKey || `g64-click-${window.crypto?.randomUUID?.() || Date.now().toString(36)}`;
    setIdempotencyKey(key);
    setBusy(true);
    try {
      const payload = {
        institution_id: institutionId.trim(),
        decisions: decisions.map((item) => ({
          decision_id: item.decisionId,
          disposition: item.disposition,
          rationale: item.rationale.trim(),
          scope: item.scope.split(',').map((value) => value.trim()).filter(Boolean),
          accountable_source_owner: item.accountableSourceOwner.trim(),
          evidence: [{
            locator: item.evidenceLocator.trim(),
            sha3_512_fingerprint: item.evidenceFingerprint.trim(),
          }],
          effective_from: toUtc(item.effectiveFrom),
          expires_or_review_at: toUtc(item.reviewAt),
          revocation_rule: item.revocationRule.trim(),
        })),
        supporting_evidence: [],
      };
      const { data } = await api.post(
        '/legal-operations/g64/ratification-workspace/records',
        payload,
        { headers: { 'Idempotency-Key': key } }
      );
      setResult(data);
      await loadHistory();
    } catch (cause) {
      setError(
        cause?.response?.data?.detail ||
        'The attestation was not confirmed by Python EOS. Check the saved history before retrying.'
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-slate-100 sm:px-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <header className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-300">
            G62 / G64 governance workspace
          </p>
          <h1 className="text-3xl font-semibold">Institutional ratification evidence</h1>
          <p className="max-w-3xl text-sm leading-6 text-slate-300">
            Each D01–D10 disposition starts undecided. The authenticated click records your
            choices for independent verification; it is not a cryptographic signature,
            institutional ratification, IAM grant, or permission to access restricted content.
          </p>
        </header>

        <section className="rounded-xl border border-amber-500/40 bg-amber-950/20 p-4" role="note">
          <h2 className="font-semibold text-amber-200">Fail-closed status</h2>
          <p className="mt-2 text-sm text-amber-100/90">
            Institution binding and ratifier authority remain unverified until the independent
            verification workflow proves them. A repository commit is evidence storage, not a signature.
            No choice in this screen activates access or claims wall enforcement.
          </p>
        </section>

        {contractError && (
          <div className="rounded-lg border border-red-500/50 p-4 text-sm text-red-200" role="alert">
            Canonical contract unavailable: {contractError}
          </div>
        )}

        {contract && (
          <section className="space-y-3 rounded-xl border border-slate-700 bg-slate-900 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Canonical contract</h2>
                <p className="mt-1 text-sm text-slate-300">{contract.contract_version}</p>
              </div>
              <span className="rounded-md border border-amber-500/50 px-2 py-1 text-xs text-amber-200">
                {contract.contract_status}
              </span>
            </div>
            <p className="break-all font-mono text-xs text-slate-400">
              SHA3-512: {contract.contract_sha3_512_fingerprint}
            </p>
            <details className="rounded-lg border border-slate-700 p-3">
              <summary className="cursor-pointer text-sm font-medium">Read full contract text</summary>
              <pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap text-xs leading-5 text-slate-300">
                {contract.contract_text}
              </pre>
            </details>
          </section>
        )}

        <form onSubmit={submitAttestation} className="space-y-5">
          <section className="space-y-2 rounded-xl border border-slate-700 bg-slate-900 p-4">
            <label htmlFor="g64-institution" className="block text-sm font-medium">
              Institution identifier label
            </label>
            <input
              id="g64-institution"
              value={institutionId}
              onChange={(event) => {
                setInstitutionId(event.target.value);
                setHistory([]);
                setResult(null);
              }}
              required
              maxLength={256}
              className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm"
              placeholder="Institution identifier from your governing records"
            />
            <p className="text-xs leading-5 text-amber-200/90">
              This is a requested evidence label only. Python EOS explicitly marks the institution
              binding as unverified; do not treat this field as proof of institutional identity.
            </p>
          </section>

          <section className="space-y-3">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold">D01–D10 dispositions</h2>
                <p className="mt-1 text-sm text-slate-300">
                  Complete each decision explicitly. No disposition is preselected.
                </p>
              </div>
              <p className="text-sm text-slate-300">{completeCount} of 10 complete</p>
            </div>

            {decisions.map((item) => (
              <details key={item.decisionId} className="rounded-xl border border-slate-700 bg-slate-900">
                <summary className="cursor-pointer list-inside p-4">
                  <span className="font-mono text-cyan-300">{item.decisionId}</span>
                  <span className="ml-3 font-medium">{item.decisionName}</span>
                  <span className="ml-2 text-xs text-slate-400">
                    {item.disposition || 'UNDECIDED'}
                  </span>
                </summary>
                <div className="grid gap-4 border-t border-slate-700 p-4 md:grid-cols-2">
                  <label className="space-y-1 text-sm">
                    <span className="block">Disposition *</span>
                    <select
                      required
                      value={item.disposition}
                      onChange={(event) => updateDecision(item.decisionId, 'disposition', event.target.value)}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2"
                    >
                      <option value="">Choose disposition</option>
                      <option value="APPROVE">APPROVE</option>
                      <option value="REJECT">REJECT</option>
                      <option value="DEFER">DEFER</option>
                    </select>
                  </label>
                  <label className="space-y-1 text-sm">
                    <span className="block">Accountable source owner *</span>
                    <input
                      required
                      value={item.accountableSourceOwner}
                      onChange={(event) => updateDecision(item.decisionId, 'accountableSourceOwner', event.target.value)}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2"
                    />
                  </label>
                  <label className="space-y-1 text-sm md:col-span-2">
                    <span className="block">Rationale *</span>
                    <textarea
                      required
                      value={item.rationale}
                      onChange={(event) => updateDecision(item.decisionId, 'rationale', event.target.value)}
                      rows={3}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2"
                    />
                  </label>
                  <label className="space-y-1 text-sm md:col-span-2">
                    <span className="block">Explicit scope (comma-separated) *</span>
                    <input
                      required
                      value={item.scope}
                      onChange={(event) => updateDecision(item.decisionId, 'scope', event.target.value)}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2"
                      placeholder="Exact role, operation, institution or matter scope"
                    />
                  </label>
                  <label className="space-y-1 text-sm">
                    <span className="block">Evidence locator *</span>
                    <input
                      required
                      value={item.evidenceLocator}
                      onChange={(event) => updateDecision(item.decisionId, 'evidenceLocator', event.target.value)}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2"
                      placeholder="Opaque source reference"
                    />
                  </label>
                  <label className="space-y-1 text-sm">
                    <span className="block">Evidence SHA3-512 fingerprint *</span>
                    <input
                      required
                      value={item.evidenceFingerprint}
                      onChange={(event) => updateDecision(item.decisionId, 'evidenceFingerprint', event.target.value.trim().toLowerCase())}
                      pattern="[0-9a-fA-F]{128}"
                      minLength={128}
                      maxLength={128}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 font-mono text-xs"
                    />
                  </label>
                  <label className="space-y-1 text-sm">
                    <span className="block">Effective from *</span>
                    <input
                      required
                      type="datetime-local"
                      value={item.effectiveFrom}
                      onChange={(event) => updateDecision(item.decisionId, 'effectiveFrom', event.target.value)}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2"
                    />
                  </label>
                  <label className="space-y-1 text-sm">
                    <span className="block">Expiry / review time *</span>
                    <input
                      required
                      type="datetime-local"
                      value={item.reviewAt}
                      onChange={(event) => updateDecision(item.decisionId, 'reviewAt', event.target.value)}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2"
                    />
                  </label>
                  <label className="space-y-1 text-sm md:col-span-2">
                    <span className="block">Revocation rule *</span>
                    <textarea
                      required
                      value={item.revocationRule}
                      onChange={(event) => updateDecision(item.decisionId, 'revocationRule', event.target.value)}
                      rows={2}
                      className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2"
                    />
                  </label>
                </div>
              </details>
            ))}
          </section>

          <section className="space-y-3 rounded-xl border border-slate-700 bg-slate-900 p-4">
            <label className="flex items-start gap-3 text-sm leading-6">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(event) => setConfirmed(event.target.checked)}
                className="mt-1"
              />
              <span>
                I confirm that I am recording these explicit choices as an authenticated click-to-attest
                event. I understand that this event is not a cryptographic signature, does not prove my
                institutional authority, does not complete ratification, and does not activate access.
              </span>
            </label>
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="submit"
                disabled={!canSubmit}
                className="rounded-lg bg-cyan-300 px-4 py-2 font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {busy ? 'Persisting evidence…' : 'Attest choices and persist evidence'}
              </button>
              <button
                type="button"
                onClick={loadHistory}
                disabled={!institutionId.trim() || busy}
                className="rounded-lg border border-slate-600 px-4 py-2 text-sm disabled:opacity-40"
              >
                Load saved evidence
              </button>
              <span className="text-xs text-slate-400">
                {completeCount === 10 ? 'All dispositions explicitly selected' : 'All 10 dispositions are required'}
              </span>
            </div>
          </section>
        </form>

        {error && (
          <div className="rounded-lg border border-red-500/50 bg-red-950/30 p-4 text-sm text-red-200" role="alert">
            {error}
          </div>
        )}

        {result && (
          <section className="space-y-3 rounded-xl border border-emerald-700/50 bg-emerald-950/20 p-4">
            <h2 className="text-lg font-semibold">Evidence submission result</h2>
            <p className="break-all font-mono text-xs text-slate-300">
              Record: {result.record?.record_id}
            </p>
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-slate-400">Application persistence</dt>
                <dd>{result.application_persistence_status || 'PERSISTED'}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Repository persistence</dt>
                <dd>{result.repository_persistence_status || 'NOT_CONFIRMED'}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Institution binding</dt>
                <dd>{result.institution_binding_status}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Ratifier authority</dt>
                <dd>{result.ratifier_authority_status}</dd>
              </div>
            </dl>
            <p className="text-sm text-amber-200">
              Ratification complete: NO. Operational access enabled: NO.
            </p>
            {result.repository_persistence_status?.startsWith('PENDING') && (
              <p className="text-sm text-amber-100">
                Application evidence is saved, but repository persistence is pending configuration or retry.
                Do not treat this as complete until the repository status is confirmed.
              </p>
            )}
          </section>
        )}

        <G64ReviewWorkflow
          institutionId={institutionId.trim()}
          recordId={result?.record?.record_id || ''}
          recordFingerprint={result?.record?.evidence_sha3_512 || ''}
        />

        {historyError && (
          <div className="rounded-lg border border-amber-500/50 p-4 text-sm text-amber-100" role="alert">
            {historyError}
          </div>
        )}

        {history.length > 0 && (
          <section className="space-y-3 rounded-xl border border-slate-700 bg-slate-900 p-4">
            <h2 className="text-lg font-semibold">Saved evidence history</h2>
            <ul className="space-y-2">
              {history.map((item) => (
                <li key={item.record?.record_id} className="rounded-lg border border-slate-700 p-3">
                  <p className="break-all font-mono text-xs">{item.record?.record_id}</p>
                  <p className="mt-1 text-sm">{item.record?.state}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    {item.institution_binding_status} · {item.ratifier_authority_status}
                  </p>
                  <button
                    type="button"
                    onClick={() => setResult(item)}
                    className="mt-2 rounded-md border border-slate-600 px-3 py-1 text-xs"
                  >
                    Open review workflow for this record
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </main>
  );
}
