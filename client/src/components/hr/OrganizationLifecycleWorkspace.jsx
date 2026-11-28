/**
 * TITLE: WILSY OS Department Lifecycle Workspace
 * VERSION: v1.0.0-M03-HR03-CHANGE-CLIENT
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Read and execute authorized department changes, history and impact with exact-tenant readback; no browser authorization.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/hr/OrganizationLifecycleWorkspace.jsx
 * COLLABORATION / OWNERSHIP: WILSY OS HR Organization / Python EOS engineering
 * CERTIFICATION / UPDATE DATE: 2026-11-28
 * CHANGELOG: v1.0.0-M03-HR03-CHANGE-CLIENT adds governed source, consumer and evidence contracts without expanding IAM grants.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
 * SECURITY / PRIVACY POSTURE: Bounded readback and event labels; no personnel/financial secrets, no fabricated external entity verification.
 * TENANT BOUNDARY: Exact authenticated EOS tenant; no root or Owner fallback.
 * AUTHORITY BOUNDARY: EOS source grants are separately required; maker and checker cannot be the same principal.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import api from '../../services/api';
import styles from './OrganizationLifecycleWorkspace.module.css';

const ROOT = '/hr/workforce/structure';
const emptyState = {items: [], status: 'PENDING', error: ''};

function verifyList(data, tenantId) {
  return data?.schema === 'WILSY-HR-ORGANIZATION-CHANGES/V1'
    && data?.source === 'EOS_HR_ORGANIZATION_CHANGES'
    && data?.tenant_id === tenantId
    && Number.isSafeInteger(data.count)
    && Array.isArray(data.items) && data.items.length === data.count
    && data.items.length <= 200
    && data.items.every(row => typeof row.change_id === 'string'
      && typeof row.record_id === 'string'
      && Number.isSafeInteger(row.revision) && row.revision > 0);
}

export default function OrganizationLifecycleWorkspace({tenantId, scopeKey, structure, onUpdated}) {
  const [queue, setQueue] = useState(emptyState);
  const [metrics, setMetrics] = useState(null);
  const [staffingReconciliation, setStaffingReconciliation] = useState({status:'PENDING',data:null});
  const [draft, setDraft] = useState({
    record_id: '', change_type: 'AMEND', name: '', parent_id: '', clear_parent: false,
    effective_from: '', reason: '',
  });
  const [selection, setSelection] = useState('');
  const [history, setHistory] = useState(null);
  const [impact, setImpact] = useState(null);
  const [asOfDate, setAsOfDate] = useState('');
  const [asOfVersion, setAsOfVersion] = useState(null);
  const [reasonById, setReasonById] = useState({});
  const [pending, setPending] = useState(false);
  const [notice, setNotice] = useState('');
  const [openEditor, setOpenEditor] = useState(false);
  const sequence = useRef(0);
  const commandKeys = useRef(new Map());
  const snapshot = useRef(scopeKey);
  snapshot.current = scopeKey;
  const departments = (structure?.items || []).filter(item => item.kind === 'DEPARTMENT');

  const headers = useCallback(() => ({'X-Tenant-ID': tenantId}), [tenantId]);
  const load = useCallback(async () => {
    if (!tenantId || !scopeKey) return null;
    const current = ++sequence.current;
    setQueue(emptyState);
    try {
      const [result, productivity] = await Promise.all([
        api.get(ROOT + '/changes', {headers: headers()}),
        api.get(ROOT + '/productivity', {headers: headers()}),
      ]);
      if (current !== sequence.current || snapshot.current !== scopeKey) return null;
      if (!verifyList(result.data, tenantId) ||
          productivity.data?.schema !== 'WILSY-HR-ORGANIZATION-PRODUCTIVITY/V1' ||
          productivity.data?.tenant_id !== tenantId ||
          productivity.data?.source !== 'EOS_ORGANIZATION_CHANGE_EVENTS') {
        throw new Error('ORGANIZATION_LIFECYCLE_SOURCE_INVALID');
      }
      setQueue({status:'VERIFIED', items:result.data.items, error:''});
      setMetrics(productivity.data);
      return result.data.items;
    } catch (error) {
      if (current !== sequence.current || snapshot.current !== scopeKey) return null;
      setQueue({status:error?.response?.status === 403 ? 'DENIED' : 'UNAVAILABLE', items:[], error:
        error?.response?.status === 403 ? 'ORGANIZATION_READ_PERMISSION_DENIED' : 'ORGANIZATION_CHANGE_SOURCE_UNAVAILABLE'});
      setMetrics(null);
      return null;
    }
  }, [scopeKey, tenantId, headers]);

  useEffect(() => {
    commandKeys.current.clear();
    setOpenEditor(false);
    setDraft({record_id:'',change_type:'AMEND',name:'',parent_id:'',clear_parent:false,effective_from:'',reason:''});
    setSelection('');
    setHistory(null);
    setImpact(null);
    setAsOfDate('');
    setAsOfVersion(null);
    setNotice('');
    void load();
    return () => {sequence.current += 1;};
  }, [load]);

  useEffect(() => {
    if (!tenantId || !scopeKey) return undefined;
    let cancelled = false;
    setStaffingReconciliation({status:'PENDING',data:null});
    void api.get(ROOT + '/staffing-reconciliation', {headers:headers()})
      .then(reply => {
        if (cancelled || snapshot.current !== scopeKey) return;
        const data = reply?.data;
        const valid = data?.schema === 'WILSY-HR-STAFFING-RECONCILIATION/V1'
          && data?.tenant_id === tenantId
          && data?.source === 'EOS_LEGACY_EMPLOYEE_DEPARTMENT_LABELS'
          && data?.reconciliation_kind === 'READ_ONLY_OBSERVATION'
          && data?.employee_assignment_linkage_certified === false
          && data?.retirement_approval_permitted === false
          && Number.isSafeInteger(data?.unmatched_active_employees)
          && Number.isSafeInteger(data?.ambiguous_active_employees)
          && Number.isSafeInteger(data?.source_total_active)
          && Array.isArray(data?.candidate_matches)
          && data.candidate_matches.length <= 200
          && data.candidate_matches.every(item =>
            typeof item.department_id === 'string'
            && Number.isSafeInteger(item.employee_count)
            && item.relationship === 'LABEL_CANDIDATE_NOT_AUTHORIZED_ASSIGNMENT');
        setStaffingReconciliation(valid ? {status:'VERIFIED',data} :
          {status:'UNAVAILABLE',data:null});
      }).catch(error => {
        if (cancelled || snapshot.current !== scopeKey) return;
        setStaffingReconciliation({
          status:error?.response?.status === 403 ? 'DENIED' : 'UNAVAILABLE',
          data:null,
        });
      });
    return () => {cancelled = true;};
  }, [scopeKey,tenantId,headers]);

  const select = async id => {
    setSelection(id);
    setImpact(null); setHistory(null); setAsOfVersion(null);
    if (!id) return;
    const current = sequence.current;
    try {
      const [impactRead, historyRead] = await Promise.all([
        api.get(ROOT + '/departments/' + encodeURIComponent(id) + '/impact', {headers: headers()}),
        api.get(ROOT + '/departments/' + encodeURIComponent(id) + '/history', {headers: headers()}),
      ]);
      if (current !== sequence.current || snapshot.current !== scopeKey) return;
      if (impactRead.data?.tenant_id !== tenantId || impactRead.data?.record_id !== id ||
          impactRead.data?.schema !== 'WILSY-HR-ORGANIZATION-IMPACT/V1' ||
          historyRead.data?.tenant_id !== tenantId || historyRead.data?.record_id !== id ||
          historyRead.data?.schema !== 'WILSY-HR-ORGANIZATION-HISTORY/V1') {
        throw new Error('ORGANIZATION_IMPACT_INVALID');
      }
      setImpact(impactRead.data);
      setHistory(historyRead.data);
    } catch(error) {
      if (current !== sequence.current || snapshot.current !== scopeKey) return;
      setNotice(error?.response?.status === 403
        ? 'This capacity cannot inspect organizational impact.'
        : 'Impact and history could not be verified. Change actions must not proceed.');
    }
  };

  const inspectAsOf = async () => {
    if (!selection || !asOfDate) return;
    const scope = scopeKey;
    setAsOfVersion(null);
    try {
      const read = await api.get(ROOT + '/departments/' + encodeURIComponent(selection) +
        '/as-of', {headers:headers(),params:{on:asOfDate}});
      if (snapshot.current !== scope) return;
      if (read.data?.schema !== 'WILSY-HR-ORGANIZATION-AS-OF/V1' ||
          read.data?.tenant_id !== tenantId ||
          read.data?.record_id !== selection ||
          read.data?.as_of !== asOfDate ||
          typeof read.data?.record?.name !== 'string') {
        throw new Error('ORGANIZATION_HISTORICAL_READ_UNVERIFIED');
      }
      setAsOfVersion(read.data.record);
    } catch(error) {
      if (snapshot.current !== scope) return;
      setNotice(error?.response?.status === 404
        ? 'No verified department version exists for that date.'
        : 'Historical department state could not be verified.');
    }
  };

  const send = async (path, payload, expected) => {
    if (pending || !scopeKey || !tenantId) return;
    const scope = scopeKey;
    const signature = JSON.stringify({scope, path, payload});
    const key = commandKeys.current.get(signature) || crypto.randomUUID();
    commandKeys.current.set(signature, key);
    setPending(true);
    setNotice('Saving in EOS and verifying persisted readback…');
    try {
      const reply = await api.post(path, payload, {headers: {
        ...headers(), 'Idempotency-Key': key,
      }});
      if (snapshot.current !== scope) return;
      if (reply.data?.schema !== 'WILSY-HR-ORGANIZATION-CHANGE/V1' ||
          reply.data?.tenant_id !== tenantId || !reply.data?.change?.change_id) {
        throw new Error('ORGANIZATION_COMMAND_RESPONSE_INVALID');
      }
      const readback = await api.get(ROOT + '/changes', {headers: headers()});
      if (snapshot.current !== scope) return;
      if (!verifyList(readback.data, tenantId) ||
          !readback.data.items.some(item => item.change_id === reply.data.change.change_id
            && item.revision === reply.data.change.revision
            && item.status === reply.data.change.status)) {
        throw new Error('ORGANIZATION_COMMAND_READBACK_UNVERIFIED');
      }
      if (expected === 'ACTIVATE' || expected === 'DECIDE') {
        // An acknowledged decision is not enough: require current registry read.
        const source = await api.get(ROOT, {headers: headers()});
        if (source.data?.tenant_id !== tenantId ||
            source.data?.schema !== 'WILSY-HR-ORGANIZATION-REGISTRY/V1') {
          throw new Error('ORGANIZATION_SOURCE_READBACK_UNVERIFIED');
        }
      }
      commandKeys.current.delete(signature);
      setQueue({status:'VERIFIED',items:readback.data.items,error:''});
      setNotice('Verified in EOS · ' + reply.data.change.status.replaceAll('_', ' ').toLowerCase());
      setOpenEditor(false);
      onUpdated?.();
      void load();
    } catch (error) {
      if (snapshot.current !== scope) return;
      setNotice(error?.response?.status === 403
        ? 'Denied by EOS organization authorization. No fallback was attempted.'
        : error?.response?.status === 409
          ? 'Source revision or dependency conflict. Refresh and inspect impact.'
          : 'Command not verified. No approval or saved state is claimed.');
    } finally {
      if (snapshot.current === scope) setPending(false);
    }
  };

  const submitDraft = event => {
    event.preventDefault();
    const target = departments.find(item => item.record_id === draft.record_id && item.status === 'APPROVED');
    if (!target || !impact || impact.record_id !== target.record_id || !history ||
        draft.reason.trim().length < 5 ||
        (draft.change_type === 'AMEND' && !draft.name.trim() && !draft.parent_id && !draft.clear_parent)) {
      setNotice('Choose an approved department, inspect verified impact, and provide the proposed change and reason.');
      return;
    }
    if (draft.change_type === 'RETIRE' && impact.retirement_blocked) {
      setNotice('Retirement is blocked by approved dependent positions or departments.');
      return;
    }
    void send(ROOT + '/departments/' + encodeURIComponent(draft.record_id) + '/changes',
      {change_type:draft.change_type,
       ...(draft.change_type === 'AMEND' && draft.name.trim() ? {name:draft.name.trim()} : {}),
       ...(draft.change_type === 'AMEND' && draft.parent_id && !draft.clear_parent ? {parent_id:draft.parent_id} : {}),
       ...(draft.change_type === 'AMEND' && draft.clear_parent ? {clear_parent:true} : {}),
       effective_from:draft.effective_from,reason:draft.reason.trim()});
  };

  return <section className={styles.lifecycle} aria-label="Governed department lifecycle">
    <div className={styles.heading}>
      <div>
        <strong>Department lifecycle</strong>
        <p>Governed amendments, future changes, retirement, historical versions and impact checks</p>
      </div>
      <button type="button" onClick={() => void load()} disabled={pending}>Refresh lifecycle</button>
    </div>
    {queue.status === 'PENDING' && <p role="status">Verifying department change authority…</p>}
    {queue.status === 'DENIED' && <p role="alert">Department change history is denied to this operating capacity.</p>}
    {queue.status === 'UNAVAILABLE' && <p role="status">Change records could not be verified. No zero result is inferred.</p>}
    {queue.status === 'VERIFIED' && <>
      <div className={styles.reconciliation} aria-label="Employee department linkage reconciliation">
        <strong>Workforce linkage</strong>
        {staffingReconciliation.status === 'PENDING' &&
          <p role="status">Checking the independently authorized employee source…</p>}
        {staffingReconciliation.status === 'DENIED' &&
          <p role="status">Employee source permission denied. No staffing relationship is inferred.</p>}
        {staffingReconciliation.status === 'UNAVAILABLE' &&
          <p role="status">Employee department linkage cannot be verified. Retirement remains blocked.</p>}
        {staffingReconciliation.status === 'VERIFIED' && <>
          <p>{staffingReconciliation.data.source_total_active} active employee records in the bounded source grouping,
            {' '}{staffingReconciliation.data.unmatched_active_employees} unmatched and
            {' '}{staffingReconciliation.data.ambiguous_active_employees} ambiguous by department label.</p>
          <p>Candidate label matches: {staffingReconciliation.data.candidate_matches.length} groups.
            These are observations, not canonical employee assignments or permission to retire a department.</p>
        </>}
      </div>
      <div className={styles.actions}>
        <button type="button" onClick={() => setOpenEditor(open => !open)} disabled={!departments.some(d => d.status === 'APPROVED')}>
          {openEditor ? 'Close change draft' : 'Propose a department change'}
        </button>
        <span>{queue.items.length} verified change proposals</span>
      </div>
      <div className={styles.inspector} aria-label="Department impact and historical reporting">
        <label>Inspect a department
          <select value={selection} onChange={event => void select(event.target.value)}>
            <option value="">Choose a source-verified department</option>
            {departments.map(dep => <option key={dep.record_id} value={dep.record_id}>
              {dep.name} · {dep.record_id} · {dep.status}
            </option>)}
          </select>
        </label>
        {selection && impact && history && <>
          <p><strong>Impact:</strong> {impact.dependent_positions.length} approved positions and
            {' '}{impact.dependent_departments.length} child departments.
            {impact.retirement_blocked
              ? ' Retirement blocked: verified structure dependencies or unverified employee assignment links.'
              : ' No retirement blockers found.'}
          </p>
          <div className={styles.history}>
            <strong>Effective-version history · {history.count} recorded revisions</strong>
            {history.items.map(version => <div key={version.revision}>
              Revision {version.revision} · {version.name} · {version.status} ·
              {' '}effective {String(version.effective_from)}
            </div>)}
            {history.count === 0 && <p>No historical amendments have been recorded yet.</p>}
          </div>
          <div className={styles.asOf}>
            <label>As of date
              <input type="date" value={asOfDate}
                onChange={event => {setAsOfDate(event.target.value);setAsOfVersion(null);}}/>
            </label>
            <button type="button" onClick={() => void inspectAsOf()} disabled={!asOfDate}>Inspect verified snapshot</button>
            {asOfVersion && <p role="status">On {asOfDate}: {asOfVersion.name} ·
              {' '}{asOfVersion.status} · Revision {asOfVersion.revision}</p>}
          </div>
        </>}
      </div>
      {openEditor && <form className={styles.form} onSubmit={submitDraft} aria-label="Department lifecycle change form">
        <label>Approved department
          <select required value={draft.record_id} onChange={event => {
            setDraft(previous => ({...previous,record_id:event.target.value,parent_id:'',clear_parent:false}));
            void select(event.target.value);
          }}>
            <option value="">Choose an approved department</option>
            {departments.filter(d => d.status === 'APPROVED').map(d =>
              <option value={d.record_id} key={d.record_id}>{d.name} · {d.record_id}</option>)}
          </select>
        </label>
        <label>Change
          <select value={draft.change_type} onChange={event => setDraft(previous => ({...previous,change_type:event.target.value}))}>
            <option value="AMEND">Amend department</option>
            <option value="RETIRE">Retire department</option>
          </select>
        </label>
        {draft.change_type === 'AMEND' && <>
          <label>New name (optional)
            <input maxLength={180} value={draft.name} onChange={event => setDraft(previous => ({...previous,name:event.target.value}))}/>
          </label>
          <label>Move under approved parent (optional)
            <select value={draft.parent_id} disabled={draft.clear_parent} onChange={event => setDraft(previous => ({...previous,parent_id:event.target.value}))}>
              <option value="">Keep current hierarchy</option>
              {departments.filter(d => d.status === 'APPROVED' && d.record_id !== draft.record_id).map(d =>
                <option key={d.record_id} value={d.record_id}>{d.name} · {d.record_id}</option>)}
            </select>
          </label>
          <label className={styles.checkboxLabel}>
            <input type="checkbox" checked={draft.clear_parent}
              onChange={event => setDraft(previous => ({
                ...previous,clear_parent:event.target.checked,parent_id:'',
              }))}/>
            Move department to top level
          </label>
        </>}
        <label>Effective date
          <input type="date" required value={draft.effective_from}
            onChange={event => setDraft(previous => ({...previous,effective_from:event.target.value}))}/>
        </label>
        <label>Business justification
          <textarea required minLength={5} maxLength={2000} value={draft.reason}
            onChange={event => setDraft(previous => ({...previous,reason:event.target.value}))}/>
        </label>
        {impact && <div className={styles.impact} role="status">
          <strong>Verified impact</strong>
          <span>{impact.dependent_positions.length} approved positions · {impact.dependent_departments.length} child departments</span>
          {impact.retirement_blocked && <span>Retirement blocked: approved dependents or employee-assignment linkage are not yet cleared.</span>}
          <span>{history?.count ?? 'Unverified'} historical versions</span>
        </div>}
        <button type="submit" disabled={pending || !impact || !history ||
          (draft.change_type === 'RETIRE' && impact.retirement_blocked)}>Save change draft</button>
      </form>}
      <div className={styles.queue}>
        {queue.items.map(change => <article key={change.change_id} className={styles.item}>
          <div><strong>{change.record_id}</strong> · {change.change_type}
            <p>{change.status.replaceAll('_',' ')} · effective {change.effective_from}</p>
          </div>
          <div className={styles.rowActions}>
            {change.status === 'DRAFT' && change.current_principal_is_maker &&
              <button type="button" disabled={pending}
                onClick={() => void send(ROOT + '/departments/' + encodeURIComponent(change.record_id) +
                  '/changes/' + encodeURIComponent(change.change_id) + '/submit',
                  {expected_revision:change.revision})}>Submit for review</button>}
            {change.status === 'SUBMITTED' && !change.current_principal_is_maker && <>
              <input aria-label={'Decision reason for ' + change.change_id} placeholder="Independent review reason"
                value={reasonById[change.change_id] || ''} onChange={event =>
                  setReasonById(previous => ({...previous,[change.change_id]:event.target.value}))}/>
              {['APPROVE','REJECT'].map(decision => <button key={decision} type="button"
                disabled={pending || (reasonById[change.change_id] || '').trim().length < 5}
                onClick={() => void send(ROOT + '/departments/' + encodeURIComponent(change.record_id) +
                  '/changes/' + encodeURIComponent(change.change_id) + '/decision',
                  {expected_revision:change.revision, decision,
                   reason:reasonById[change.change_id].trim()}, 'DECIDE')}>
                {decision === 'APPROVE' ? 'Approve' : 'Reject'}
              </button>)}
            </>}
            {change.status === 'APPROVED_SCHEDULED' && !change.current_principal_is_maker &&
              <button type="button" disabled={pending}
                onClick={() => void send(ROOT + '/departments/' + encodeURIComponent(change.record_id) +
                  '/changes/' + encodeURIComponent(change.change_id) + '/activate', {}, 'ACTIVATE')}>
                Activate when due
              </button>}
          </div>
        </article>)}
        {!queue.items.length && <p>No department changes recorded in this tenant.</p>}
      </div>
      {metrics && <div className={styles.metrics}>
        <strong>Source activity</strong>
        <span>{metrics.change_drafts} change drafts</span>
        <span>{metrics.approved_changes} approvals · {metrics.rejected_changes} rejections</span>
        <span>{metrics.mean_draft_to_decision_seconds === null
          ? 'Decision duration not yet measurable'
          : 'Mean draft-to-decision: ' + Math.round(metrics.mean_draft_to_decision_seconds / 60) + ' min'}</span>
        {metrics.client_observation_sample > 0 && <>
          <span>Manual fields: {metrics.client_observed?.MANUAL_FIELD_EDITED ?? 0}</span>
          <span>Validation failures: {metrics.client_observed?.VALIDATION_FAILED ?? 0}</span>
          <span>Template selections: {metrics.client_observed?.CATALOG_SELECTED ?? 0}</span>
          <span>{metrics.client_mean_form_to_verified_seconds == null
            ? 'Form completion duration unavailable'
            : 'Mean form-to-verified draft: ' + metrics.client_mean_form_to_verified_seconds + 's'}</span>
        </>}
        <small>Approval timings: EOS source events. Form effort: client-reported,
          bounded and non-identifying ({metrics.client_observation_sample ?? 0} observations).
          Accessibility audit results remain unverified.</small>
      </div>}
    </>}
    {notice && <p role="status" className={styles.notice}>{notice}</p>}
  </section>;
}

/**
 * ARTIFACT: client/src/components/hr/OrganizationLifecycleWorkspace.jsx
 * VERSION: v1.0.0-M03-HR03-CHANGE-CLIENT
 * AUTHORITY BOUNDARY: Presentation/projection only; Python EOS owns authorizations and decisions.
 * TENANT POSTURE: Exact authorized tenant only; no cross-tenant records, Owner or root fallback.
 * FAIL-CLOSED POSTURE: Missing or contradictory evidence is denied/unavailable, never approved.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
