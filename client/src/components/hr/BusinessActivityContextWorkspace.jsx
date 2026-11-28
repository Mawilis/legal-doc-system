/**
 * TITLE: WILSY OS Business Activity Context Workspace
 * VERSION: v1.0.0-M03-HR03-BUSINESS-CONTEXT-CLIENT
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Multi-activity profile proposals, submissions and independent decisions using EOS-only verified responses.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/hr/BusinessActivityContextWorkspace.jsx
 * COLLABORATION / OWNERSHIP: WILSY OS HR Organization / Python EOS engineering
 * CERTIFICATION / UPDATE DATE: 2026-11-28
 * CHANGELOG: v1.0.0-M03-HR03-BUSINESS-CONTEXT-CLIENT adds governed source, consumer and evidence contracts without expanding IAM grants.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
 * SECURITY / PRIVACY POSTURE: Bounded readback and event labels; no personnel/financial secrets, no fabricated external entity verification.
 * TENANT BOUNDARY: Exact authenticated EOS tenant; no root or Owner fallback.
 * AUTHORITY BOUNDARY: EOS source grants are separately required; maker and checker cannot be the same principal.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
 */
import React, {useCallback, useEffect, useRef, useState} from 'react';
import api from '../../services/api';
import {ORGANIZATION_BUSINESS_MODELS} from './organizationDepartmentCatalog.js';
import styles from './BusinessActivityContextWorkspace.module.css';

const ROOT = '/hr/workforce/structure/context';
const allowed = new Set(ORGANIZATION_BUSINESS_MODELS.map(m => m.id));

function valid(data, tenantId) {
  return data?.schema === 'WILSY-HR-BUSINESS-ACTIVITY-CONTEXT/V1'
    && data?.source === 'EOS_APPROVED_TENANT_BUSINESS_ACTIVITIES'
    && data?.tenant_id === tenantId
    && ['APPROVED','UNCONFIGURED'].includes(data.status)
    && Number.isSafeInteger(data.revision)
    && Array.isArray(data.activity_ids)
    && data.activity_ids.every(id => allowed.has(id))
    && Array.isArray(data.proposals)
    && data.proposals.length <= 100
    && data.proposals.every(p => typeof p.proposal_id === 'string'
      && Number.isSafeInteger(p.revision));
}

export default function BusinessActivityContextWorkspace({tenantId, scopeKey, onApproved}) {
  const [state, setState] = useState({status:'PENDING', data:null});
  const [editing, setEditing] = useState(false);
  const [activities, setActivities] = useState([]);
  const [reason, setReason] = useState('');
  const [reviewReasons, setReviewReasons] = useState({});
  const [notice, setNotice] = useState('');
  const [pending, setPending] = useState(false);
  const token = useRef(0);
  const keys = useRef(new Map());
  const approvedCallback = useRef(onApproved);
  approvedCallback.current = onApproved;
  const actualScope = useRef(scopeKey);
  actualScope.current = scopeKey;
  const headers = useCallback(() => ({'X-Tenant-ID':tenantId}), [tenantId]);

  const load = useCallback(async () => {
    if (!scopeKey || !tenantId) return null;
    const seq = ++token.current;
    try {
      const reply = await api.get(ROOT, {headers:headers()});
      if (seq !== token.current || actualScope.current !== scopeKey) return null;
      if (!valid(reply.data, tenantId)) throw Error('BUSINESS_CONTEXT_INVALID_ENVELOPE');
      setState({status:'VERIFIED',data:reply.data});
      approvedCallback.current?.(reply.data.status === 'APPROVED' ? reply.data.activity_ids : []);
      return reply.data;
    } catch(error) {
      if (seq !== token.current || actualScope.current !== scopeKey) return null;
      setState({status:error?.response?.status === 403 ? 'DENIED' : 'UNAVAILABLE',data:null});
      approvedCallback.current?.([]);
      return null;
    }
  }, [scopeKey, tenantId, headers]);

  useEffect(() => {
    keys.current.clear(); setEditing(false); setActivities([]);
    setReason(''); setReviewReasons({}); setNotice('');
    void load();
    return () => {token.current += 1;};
  }, [load]);

  const command = async (path,payload) => {
    if (pending || !scopeKey) return;
    const scope = scopeKey;
    const fingerprint = JSON.stringify({scope,path,payload});
    const key = keys.current.get(fingerprint) || crypto.randomUUID();
    keys.current.set(fingerprint,key);
    setPending(true);
    setNotice('Saving and checking EOS source…');
    try {
      const response = await api.post(path,payload,{headers:{...headers(),'Idempotency-Key':key}});
      if (actualScope.current !== scope) return;
      if (response.data?.schema !== 'WILSY-HR-BUSINESS-ACTIVITY-COMMAND/V1' ||
          response.data?.tenant_id !== tenantId || !response.data?.proposal?.proposal_id) {
        throw Error('BUSINESS_CONTEXT_COMMAND_INVALID');
      }
      const readback = await api.get(ROOT,{headers:headers()});
      if (actualScope.current !== scope) return;
      if (!valid(readback.data,tenantId) ||
          !readback.data.proposals.some(row => row.proposal_id === response.data.proposal.proposal_id &&
            row.revision === response.data.proposal.revision &&
            row.status === response.data.proposal.status)) {
        throw Error('BUSINESS_CONTEXT_READBACK_UNVERIFIED');
      }
      if (response.data.proposal.status === 'APPROVED' &&
        !response.data.proposal.activity_ids.every(id => readback.data.activity_ids.includes(id))) {
        throw Error('BUSINESS_CONTEXT_ACTIVATION_NOT_VERIFIED');
      }
      keys.current.delete(fingerprint);
      setState({status:'VERIFIED',data:readback.data});
      approvedCallback.current?.(readback.data.status === 'APPROVED' ? readback.data.activity_ids : []);
      setEditing(false);
      setNotice('Verified in EOS · ' + response.data.proposal.status.toLowerCase());
    } catch(error) {
      if (actualScope.current !== scope) return;
      setNotice(error?.response?.status === 403
        ? 'Denied by EOS business-context authority; no fallback.'
        : 'Command or readback could not be verified. No success is claimed.');
    } finally {
      if (actualScope.current === scope) setPending(false);
    }
  };

  const data = state.data;
  return <section className={styles.context} aria-label="Governed business activity profile">
    <div className={styles.toolbar}>
      <div>
        <strong>Business context</strong>
        <p>{state.status === 'VERIFIED' && data.status === 'APPROVED'
          ? 'Approved activities help prepare department suggestions'
          : 'Classify the employer once for smarter department suggestions'}</p>
      </div>
      <button type="button" onClick={() => setEditing(value => !value)}
        disabled={state.status !== 'VERIFIED' || pending}>Manage activities</button>
    </div>
    {state.status === 'PENDING' && <p role="status">Verifying employer business context…</p>}
    {state.status === 'DENIED' && <p role="alert">Business-context read denied for this capacity.</p>}
    {state.status === 'UNAVAILABLE' && <p role="status">Employer business context could not be verified. No industry is inferred.</p>}
    {state.status === 'VERIFIED' && <>
      <p className={styles.current}>
        {data.status === 'APPROVED'
          ? data.activity_ids.map(id => ORGANIZATION_BUSINESS_MODELS.find(m => m.id === id)?.label || id).join(' · ')
          : 'No approved activity profile yet — the department catalogue remains available for manual selection.'}
      </p>
      {data.entity_status !== 'VERIFIED' && <small>Verified operating-entity linkage is not yet connected. No legal entity is inferred.</small>}
      {editing && <form className={styles.editor} aria-label="Business activity proposal form"
        onSubmit={event => {
          event.preventDefault();
          if (activities.length && reason.trim().length >= 5)
            void command(ROOT + '/proposals',{activity_ids:activities,reason:reason.trim()});
        }}>
        <p>Choose up to eight business activities. Custom departmental work remains possible across activities.</p>
        <div className={styles.choices}>
          {ORGANIZATION_BUSINESS_MODELS.map(model => <label key={model.id}>
            <input type="checkbox" checked={activities.includes(model.id)}
              disabled={!activities.includes(model.id) && activities.length >= 8}
              onChange={event => setActivities(old => event.target.checked
                ? [...old, model.id] : old.filter(id => id !== model.id))}/>
            <span>{model.label}</span>
          </label>)}
        </div>
        <label>Business justification
          <textarea required minLength={5} maxLength={1000} value={reason}
            onChange={event => setReason(event.target.value)}/>
        </label>
        <button type="submit" disabled={pending || !activities.length || reason.trim().length < 5}>
          Save activity proposal
        </button>
      </form>}
      <div className={styles.proposals}>
        {data.proposals.map(p => <div className={styles.proposal} key={p.proposal_id}>
          <div><strong>{p.status}</strong> · {p.activity_ids.length} activities
            <p>Revision {p.revision}</p></div>
          {p.status === 'DRAFT' && p.current_principal_is_maker &&
            <button type="button" disabled={pending} onClick={() => void command(
              ROOT + '/proposals/' + encodeURIComponent(p.proposal_id) + '/submit',
              {expected_revision:p.revision})}>Submit for independent review</button>}
          {p.status === 'SUBMITTED' && !p.current_principal_is_maker && <div className={styles.review}>
            <input aria-label={'Review reason '+p.proposal_id} placeholder="Reason for independent decision"
              value={reviewReasons[p.proposal_id] || ''}
              onChange={event => setReviewReasons(old => ({...old,[p.proposal_id]:event.target.value}))}/>
            {['APPROVE','REJECT'].map(decision => <button type="button" key={decision}
              disabled={pending || (reviewReasons[p.proposal_id] || '').trim().length < 5}
              onClick={() => void command(
                ROOT + '/proposals/' + encodeURIComponent(p.proposal_id) + '/decision',
                {expected_revision:p.revision, decision, reason:reviewReasons[p.proposal_id].trim()})}>
              {decision === 'APPROVE' ? 'Approve' : 'Reject'}
            </button>)}
          </div>}
        </div>)}
      </div>
    </>}
    {notice && <p className={styles.notice} role="status">{notice}</p>}
  </section>;
}

/**
 * ARTIFACT: client/src/components/hr/BusinessActivityContextWorkspace.jsx
 * VERSION: v1.0.0-M03-HR03-BUSINESS-CONTEXT-CLIENT
 * AUTHORITY BOUNDARY: Presentation/projection only; Python EOS owns authorizations and decisions.
 * TENANT POSTURE: Exact authorized tenant only; no cross-tenant records, Owner or root fallback.
 * FAIL-CLOSED POSTURE: Missing or contradictory evidence is denied/unavailable, never approved.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
