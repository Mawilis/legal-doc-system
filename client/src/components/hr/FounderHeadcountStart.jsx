/**
 * TITLE: WILSY OS First HR Leadership Headcount Command
 * VERSION: v1.1.1-WEBCRYPTO-REPLAY-IDEMPOTENCY
 * AUTHORITY: Existing Python EOS HeadcountRequisitionRouter only.
 * EPITOME: Source-verified headcount request creation for the first HR Director
 *          and Manager without asserting approval or employee admission.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/hr/FounderHeadcountStart.jsx
 * COLLABORATION / OWNERSHIP: HrDashboard authenticated scope and source readback.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG: v1.1.1-WEBCRYPTO-REPLAY-IDEMPOTENCY uses native WebCrypto entropy for replay keys without depending on randomUUID support in embedded browser/test runtimes; no noncryptographic fallback.
 * CHANGELOG: v1.1.0-HEADCOUNT-SUBMIT-TO-INDEPENDENT-REVIEW adds an existing-requisition submit command with revision CAS, exact source response and independent reviewer boundary.
 * CHANGELOG: v1.0.1-TRUTHFUL-HR-DRAFT-READBACK preserves accepted command truth when subsequent list refresh is unavailable; never represents a failed refresh as a failed submission.
 * CHANGELOG: v1.0.0-FOUNDER-FIRST-HR-HEADCOUNT wires a compact governed first-
 *            hire requisition composer to existing EOS create, with replay keys
 *            and exact-tenant response validation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: No candidate identity or pay data; no local persistence.
 * TENANT BOUNDARY: Only the verified signed-in tenant supplied by parent.
 * AUTHORITY BOUNDARY: Creation of DRAFT requisition only; approval remains independent.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React, { useEffect, useRef, useState } from 'react';
import api from '../../services/api';

const EMPTY = Object.freeze({
  position_title: 'HR Director',
  department_id: 'HR',
  employment_type: 'PERMANENT',
  work_location: '',
  headcount: 1,
  business_justification: '',
});
const issueReplayKey = () => {
  if (!globalThis.crypto || typeof globalThis.crypto.getRandomValues !== 'function') {
    throw new Error('CRYPTOGRAPHIC_IDEMPOTENCY_UNAVAILABLE');
  }
  const bytes = globalThis.crypto.getRandomValues(new Uint8Array(16));
  return 'hr-' + Array.from(bytes, value => value.toString(16).padStart(2, '0')).join('');
};
const safeCode = error => {
  const detail = error?.response?.data?.detail;
  const code = typeof detail === 'string' ? detail : error?.response?.status;
  return /^[A-Z0-9_]{3,100}$/.test(String(code)) ? String(code) : 'HEADCOUNT_COMMAND_UNVERIFIED';
};

export default function FounderHeadcountStart({ tenantId, admitted, onCreated }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ ...EMPTY });
  const [status, setStatus] = useState({ kind: 'IDLE', text: '' });
  const keyRef = useRef(null);
  const inFlight = useRef(false);
  const scopeRef = useRef(tenantId);
  useEffect(() => {
    scopeRef.current = tenantId;
    setOpen(false);
    setForm({ ...EMPTY });
    setStatus({ kind: 'IDLE', text: '' });
    keyRef.current = null;
  }, [tenantId]);
  const update = (name, value) => {
    keyRef.current = null;
    setForm(previous => ({ ...previous, [name]: value }));
    setStatus({ kind: 'IDLE', text: '' });
  };
  const submit = async event => {
    event.preventDefault();
    if (!admitted || !tenantId || inFlight.current) return;
    const payload = {
      position_title: form.position_title.trim(),
      department_id: form.department_id.trim(),
      employment_type: form.employment_type.trim(),
      work_location: form.work_location.trim(),
      headcount: 1,
      business_justification: form.business_justification.trim(),
    };
    if (Object.entries(payload).some(([key, value]) => key !== 'headcount' && !value)) {
      setStatus({ kind: 'ERROR', text: 'All requisition fields are required.' });
      return;
    }
    if (!keyRef.current) {
      try {
        keyRef.current = issueReplayKey();
      } catch {
        setStatus({ kind: 'ERROR', text: 'Secure command identifier unavailable; no request was sent.' });
        return;
      }
    }
    const requestedTenant = tenantId;
    inFlight.current = true;
    setStatus({ kind: 'PENDING', text: 'Submitting one governed draft requisition…' });
    try {
      const response = await api.post('/hr/headcount-requisitions', payload, {
        headers: { 'X-Tenant-ID': requestedTenant, 'Idempotency-Key': keyRef.current },
      });
      const result = response?.data;
      if (scopeRef.current !== requestedTenant) return;
      if (result?.tenant_id !== requestedTenant
          || !/^REQ-[A-F0-9]{24}$/.test(String(result?.requisition_id))
          || result?.status !== 'DRAFT') {
        throw new Error('HEADCOUNT_READBACK_PROVENANCE_UNVERIFIED');
      }
      setStatus({
        kind: 'ACCEPTED',
        text: 'Draft requisition accepted by EOS. Approval has not been granted.',
      });
      setOpen(false);
      keyRef.current = null;
      if (typeof onCreated === 'function') {
        try {
          await onCreated();
        } catch {
          if (scopeRef.current === requestedTenant) {
            setStatus({
              kind: 'ACCEPTED',
              text: 'EOS accepted the draft, but fresh list readback is unavailable. Refresh before further action.',
            });
          }
        }
      }
    } catch (error) {
      if (scopeRef.current !== requestedTenant) return;
      setStatus({ kind: 'ERROR', text: 'EOS did not verify the draft: ' + safeCode(error) });
    } finally {
      inFlight.current = false;
    }
  };
  return (
    <div className="w-full" data-testid="first-hr-headcount-command">
      <button type="button" disabled={!admitted || inFlight.current}
        onClick={() => setOpen(value => !value)}
        aria-expanded={open} aria-controls="first-hr-headcount-form"
        className="min-h-9 rounded-md border border-blue-300 bg-blue-50 px-3 text-xs font-semibold text-blue-900 hover:bg-blue-100 disabled:opacity-50">
        {open ? 'Close requisition' : 'Request first HR position'}
      </button>
      <p className="mt-1 text-xs text-slate-600">
        A draft request only. A different authorized person must make its independent decision.
      </p>
      {status.kind !== 'IDLE' && <p role="status" className="mt-1 text-xs text-slate-800">{status.text}</p>}
      <div id="first-hr-headcount-form" hidden={!open}>
        {open && <form onSubmit={submit} className="mt-3 grid gap-3 rounded-lg border border-slate-300 bg-white p-3 sm:grid-cols-2">
          <label className="text-xs font-semibold text-slate-800">Position
            <select aria-label="HR leadership position" value={form.position_title}
              onChange={event => update('position_title', event.target.value)}
              className="mt-1 block min-h-10 w-full rounded-md border border-slate-300 bg-white px-2 text-sm text-slate-900">
              <option value="HR Director">HR Director</option>
              <option value="HR Manager">HR Manager</option>
              <option value="HR Generalist">HR Generalist</option>
              <option value="HR Administrator">HR Administrator</option>
            </select>
          </label>
          <label className="text-xs font-semibold text-slate-800">Department identifier
            <input required maxLength={180} value={form.department_id} onChange={event => update('department_id', event.target.value)}
              className="mt-1 block min-h-10 w-full rounded-md border border-slate-300 px-2 text-sm text-slate-900" />
          </label>
          <label className="text-xs font-semibold text-slate-800">Employment type
            <select aria-label="Employment type" value={form.employment_type}
              onChange={event => update('employment_type', event.target.value)}
              className="mt-1 block min-h-10 w-full rounded-md border border-slate-300 bg-white px-2 text-sm text-slate-900">
              <option value="PERMANENT">Permanent</option>
              <option value="FIXED_TERM">Fixed term</option>
            </select>
          </label>
          <label className="text-xs font-semibold text-slate-800">Work location
            <input required maxLength={180} value={form.work_location}
              onChange={event => update('work_location', event.target.value)}
              placeholder="Employer workplace" className="mt-1 block min-h-10 w-full rounded-md border border-slate-300 px-2 text-sm text-slate-900"/>
          </label>
          <label className="text-xs font-semibold text-slate-800 sm:col-span-2">Business justification
            <textarea required maxLength={4000} rows={3} value={form.business_justification}
              onChange={event => update('business_justification', event.target.value)}
              placeholder="Why the first HR appointment is required"
              className="mt-1 block w-full rounded-md border border-slate-300 p-2 text-sm text-slate-900"/>
          </label>
          <div className="flex flex-wrap items-center gap-2 sm:col-span-2">
            <button type="submit" disabled={inFlight.current || !admitted}
              className="min-h-10 rounded-md bg-blue-800 px-4 text-xs font-semibold text-white hover:bg-blue-900 disabled:opacity-50">
              Submit draft to EOS
            </button>
            <span className="text-xs text-slate-600">One position · no automatic approval or admission</span>
          </div>
        </form>}
      </div>
    </div>
  );
}

/**
 * Submit an existing EOS draft for independent review. This does not approve,
 * admit a person or infer that the caller may also decide the requisition.
 */
export function HeadcountDraftSubmit({ tenantId, admitted, requisition, onSubmitted }) {
  const [state, setState] = useState({ kind: 'IDLE', text: '' });
  const keyRef = useRef(null);
  const inFlight = useRef(false);
  const scopeRef = useRef(tenantId);
  useEffect(() => {
    scopeRef.current = tenantId;
    keyRef.current = null;
    setState({ kind: 'IDLE', text: '' });
  }, [tenantId, requisition?.id, requisition?.revision]);

  if (!requisition || requisition.status !== 'DRAFT') return null;
  const submit = async () => {
    if (!admitted || inFlight.current || !tenantId
        || !/^REQ-[A-F0-9]{24}$/.test(String(requisition.id))
        || !Number.isSafeInteger(requisition.revision) || requisition.revision < 1) return;
    if (!keyRef.current) {
      try {
        keyRef.current = issueReplayKey();
      } catch {
        setState({ kind: 'ERROR', text: 'Secure command identifier unavailable; no request was sent.' });
        return;
      }
    }
    inFlight.current = true;
    const requestedTenant = tenantId;
    setState({ kind: 'PENDING', text: 'Submitting for independent review…' });
    try {
      const response = await api.post(
        '/hr/headcount-requisitions/' + encodeURIComponent(requisition.id) + '/submit',
        { expected_revision: requisition.revision },
        { headers: { 'X-Tenant-ID': requestedTenant, 'Idempotency-Key': keyRef.current } },
      );
      if (scopeRef.current !== requestedTenant) return;
      const record = response?.data;
      if (record?.tenant_id !== requestedTenant
          || record?.requisition_id !== requisition.id
          || record?.status !== 'SUBMITTED') {
        throw new Error('HEADCOUNT_SUBMISSION_UNVERIFIED');
      }
      setState({ kind: 'ACCEPTED', text: 'Submitted; independent decision remains outstanding.' });
      keyRef.current = null;
      if (typeof onSubmitted === 'function') {
        try {
          await onSubmitted();
        } catch {
          if (scopeRef.current === requestedTenant) {
            setState({ kind: 'ACCEPTED', text: 'Submission acknowledged; current list refresh unavailable.' });
          }
        }
      }
    } catch (error) {
      if (scopeRef.current === requestedTenant) {
        setState({ kind: 'ERROR', text: 'Submission unverified: ' + safeCode(error) });
      }
    } finally {
      inFlight.current = false;
    }
  };
  return <div className="flex flex-col items-start gap-1">
    <button type="button" disabled={!admitted || state.kind === 'PENDING'}
      onClick={submit}
      className="min-h-9 rounded-md border border-amber-400 bg-amber-50 px-3 text-xs font-semibold text-amber-950 hover:bg-amber-100 disabled:opacity-50">
      Submit for review
    </button>
    {state.kind !== 'IDLE' && <span role="status" className="text-xs text-slate-700">{state.text}</span>}
  </div>;
}

/* ARTIFACT: client/src/components/hr/FounderHeadcountStart.jsx
 * VERSION: v1.1.1-WEBCRYPTO-REPLAY-IDEMPOTENCY
 * AUTHORITY BOUNDARY: Authenticated EOS draft requisition only.
 * TENANT POSTURE: Verified tenant-bound request and response; never a fallback.
 * FAIL-CLOSED POSTURE: No approval or employee existence inferred.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
