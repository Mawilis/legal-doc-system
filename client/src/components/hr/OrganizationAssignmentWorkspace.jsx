/**
 * TITLE: WILSY OS Source-owned Workforce Assignment Workspace
 * VERSION: v1.0.0-M03-HR03-EMPLOYEE-POSITION-ASSIGNMENT-CLIENT
 * AUTHORITY: EOS employee-relation/organization IAM, never client permission claims.
 * EPITOME: Select an authorized employee and approved position, then propose,
 *          submit or independently decide durable organization assignments.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/hr/OrganizationAssignmentWorkspace.jsx
 * COLLABORATION / OWNERSHIP: WILSY OS HR People.
 * CERTIFICATION / UPDATE DATE: 2026-11-28
 * CHANGELOG: v1.0.0 adds exact-tenant readback and source-owned assignment actions.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Directory-safe display names only; no protected files.
 * TENANT BOUNDARY: Current principal/tenant selected session, no root fallback.
 * AUTHORITY BOUNDARY: Server checks both employee relation and org permissions.
 * TRANSACTION BOUNDARY: Python EOS owns all mutations and transaction consistency.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS only; no payroll or headcount grant.
 */
import React, {useCallback, useEffect, useRef, useState} from 'react';
import api from '../../services/api';
import styles from './OrganizationAssignmentWorkspace.module.css';

const ROOT = '/hr/workforce/assignments';
const empty = {status:'PENDING',data:null};
const directoryEmpty = {status:'PENDING',items:[],total:0};
const validAssignments = (data, tenant) =>
  data?.schema === 'WILSY-HR-GOVERNED-ASSIGNMENTS/V1' &&
  data?.tenant_id === tenant && data?.source === 'EOS_HR_ASSIGNMENT_REGISTRY' &&
  data?.legacy_employee_fields_synchronized === false &&
  Array.isArray(data.proposals) && data.proposals.length <= 200 &&
  Array.isArray(data.current) && data.current.length <= 200 &&
  data.proposals.every(p => typeof p.proposal_id === 'string' && Number.isSafeInteger(p.revision)) &&
  data.current.every(a => typeof a.employee_id === 'string' && typeof a.position_id === 'string');
const blank = {employee_id:'',position_id:'',effective_from:'',reason:''};

export default function OrganizationAssignmentWorkspace({tenantId,scopeKey,structure}) {
  const [state,setState] = useState(empty);
  const [directory,setDirectory] = useState(directoryEmpty);
  const [filter,setFilter] = useState('');
  const [page,setPage] = useState(0);
  const [form,setForm] = useState(blank);
  const [editing,setEditing] = useState(false);
  const [reviewReasons,setReviewReasons] = useState({});
  const [busy,setBusy] = useState(false);
  const [notice,setNotice] = useState('');
  const [history,setHistory] = useState(null);
  const [planning,setPlanning] = useState({status:'PENDING',data:null});
  const [planningPage,setPlanningPage] = useState(0);
  const counter = useRef(0), scope = useRef(scopeKey), keys = useRef(new Map());
  scope.current = scopeKey;
  const positions = (structure?.items || []).filter(p => p.kind === 'POSITION' && p.status === 'APPROVED');
  const headers = useCallback(() => ({'X-Tenant-ID':tenantId}),[tenantId]);

  const reload = useCallback(async () => {
    if(!scopeKey || !tenantId) return null;
    const nonce=++counter.current;
    try {
      const result=await api.get(ROOT,{headers:headers()});
      if(nonce!==counter.current || scope.current!==scopeKey) return null;
      if(!validAssignments(result.data,tenantId)) throw Error('HR_ASSIGNMENT_SOURCE_INVALID');
      setState({status:'VERIFIED',data:result.data});
      return result.data;
    } catch(error) {
      if(nonce!==counter.current || scope.current!==scopeKey) return null;
      setState({status:error?.response?.status===403?'DENIED':'UNAVAILABLE',data:null});
      return null;
    }
  },[scopeKey,tenantId,headers]);

  useEffect(()=>{
    keys.current.clear();
    setState(empty);setDirectory(directoryEmpty);
    setEditing(false);setNotice('');setForm(blank);setPage(0);setFilter('');
    setHistory(null);setReviewReasons({});setPlanningPage(0);
    setPlanning({status:'PENDING',data:null});
    void reload();
    return ()=>{counter.current+=1;};
  },[reload]);

  useEffect(()=>{
    if(!scopeKey || !tenantId || state.status!=='VERIFIED')return undefined;
    let cancelled=false;
    setDirectory(directoryEmpty);
    const normalized=filter.trim();
    const params={limit:50,offset:page*50};
    if(normalized.length>=2) params.q=normalized;
    void api.get('/hr/workforce',{headers:headers(),params})
      .then(reply=>{
        if(cancelled||scope.current!==scopeKey)return;
        const data=reply.data;
        if(data?.source!=='AUTHORISED_HR_EMPLOYEE_REGISTRY' ||
           !Array.isArray(data.items) || data.items.length>50 ||
           !Number.isSafeInteger(data.total) || data.total<0 ||
           !Number.isSafeInteger(data.offset) || data.offset!==page*50 ||
           !data.items.every(item=>typeof item.employeeId==='string')) {
          throw Error('HR_ASSIGNMENT_DIRECTORY_INVALID');
        }
        setDirectory({status:'VERIFIED',items:data.items,total:data.total});
      }).catch(error=>{
        if(cancelled||scope.current!==scopeKey)return;
        setDirectory({status:error?.response?.status===403?'DENIED':'UNAVAILABLE',items:[],total:0});
      });
    return ()=>{cancelled=true;};
  },[scopeKey,tenantId,state.status,filter,page,headers]);

  useEffect(()=>{
    if(!scopeKey||!tenantId||state.status!=='VERIFIED')return undefined;
    let cancelled=false;
    setPlanning({status:'PENDING',data:null});
    void api.get(ROOT+'/planning',{headers:headers(),params:{limit:50,offset:planningPage*50}})
      .then(reply=>{
        if(cancelled||scope.current!==scopeKey)return;
        const data=reply?.data;
        const verified=data?.schema==='WILSY-HR-POSITION-UTILIZATION/V1' &&
          data?.source==='EOS_APPROVED_POSITION_ASSIGNMENT_GRAPH' &&
          data?.tenant_id===tenantId &&
          data?.legacy_employee_fields_synchronized===false &&
          data?.funded_headcount_verified===false &&
          Number.isSafeInteger(data.total) && data.total>=0 &&
          data.offset===planningPage*50 &&
          Array.isArray(data.items) && data.items.length<=50 &&
          data.items.every(item=>typeof item.position_id==='string' &&
            Number.isSafeInteger(item.approved_capacity) &&
            Number.isSafeInteger(item.governed_assignments) &&
            item.unfilled_graph_slots===item.approved_capacity-item.governed_assignments);
        setPlanning(verified?{status:'VERIFIED',data}:{status:'UNAVAILABLE',data:null});
      }).catch(error=>{
        if(cancelled||scope.current!==scopeKey)return;
        setPlanning({status:error?.response?.status===403?'DENIED':'UNAVAILABLE',data:null});
      });
    return ()=>{cancelled=true;};
  },[scopeKey,tenantId,state.status,planningPage,headers]);

  const send=async(path,payload)=>{
    if(busy||state.status!=='VERIFIED')return;
    const currentScope=scopeKey;
    const signature=JSON.stringify({currentScope,path,payload});
    const key=keys.current.get(signature)||crypto.randomUUID();
    keys.current.set(signature,key);
    setBusy(true);setNotice('Verifying EOS command and durable readback…');
    try{
      const response=await api.post(path,payload,{headers:{...headers(),'Idempotency-Key':key}});
      if(scope.current!==currentScope)return;
      if(response.data?.schema!=='WILSY-HR-ASSIGNMENT-COMMAND/V1' ||
         response.data?.tenant_id!==tenantId ||
         !response.data?.proposal?.proposal_id)throw Error('HR_ASSIGNMENT_COMMAND_INVALID');
      const read=await api.get(ROOT,{headers:headers()});
      if(scope.current!==currentScope)return;
      if(!validAssignments(read.data,tenantId)||!read.data.proposals.some(p=>
         p.proposal_id===response.data.proposal.proposal_id &&
         p.revision===response.data.proposal.revision &&
         p.status===response.data.proposal.status))throw Error('HR_ASSIGNMENT_READBACK_INVALID');
      if(response.data.proposal.status==='APPROVED' &&
         !read.data.current.some(a=>
           a.employee_id===response.data.proposal.employee_id &&
           a.position_id===response.data.proposal.position_id &&
           a.department_id===response.data.proposal.department_id)) {
        throw Error('HR_ASSIGNMENT_GRAPH_READBACK_INVALID');
      }
      keys.current.delete(signature);
      setState({status:'VERIFIED',data:read.data});
      setEditing(false);setForm(blank);
      setNotice('Verified in EOS · '+response.data.proposal.status.toLowerCase());
    }catch(error){
      if(scope.current!==currentScope)return;
      setNotice(error?.response?.status===403 ?
        'EOS denied the required assignment authority. No fallback was attempted.' :
        error?.response?.status===409 ?
        'Assignment conflict, capacity or effective-date constraint. Refresh and inspect the source.' :
        'Command not verified in EOS. No saved assignment is claimed.');
    }finally{if(scope.current===currentScope)setBusy(false);}
  };

  const inspectHistory=async employeeId=>{
    const currentScope=scopeKey;
    setHistory(null);
    try{
      const read=await api.get(ROOT+'/employees/'+encodeURIComponent(employeeId)+'/history',{headers:headers()});
      if(scope.current!==currentScope)return;
      const data=read.data;
      if(data?.schema!=='WILSY-HR-ASSIGNMENT-HISTORY/V1' ||
         data?.tenant_id!==tenantId || data?.employee_id!==employeeId ||
         !Array.isArray(data.items) || data.items.length!==data.count ||
         data.count>200)throw Error('HR_ASSIGNMENT_HISTORY_INVALID');
      setHistory(data);
    }catch(error){
      if(scope.current!==currentScope)return;
      setNotice(error?.response?.status===403?
        'Assignment history denied by EOS.' : 'Assignment history could not be verified.');
    }
  };

  return <section className={styles.workspace} aria-label="Governed employee assignments">
    <div className={styles.header}>
      <div><strong>Employee → position assignments</strong>
        <p>Governed position changes and effective-dated staffing relationships</p>
      </div>
      <button type="button" disabled={busy} onClick={()=>void reload()}>Refresh assignments</button>
    </div>
    {state.status==='PENDING'&&<p role="status">Checking assignment authority…</p>}
    {state.status==='DENIED'&&<p role="alert">Assignments denied to this capacity. No Owner fallback.</p>}
    {state.status==='UNAVAILABLE'&&<p role="status">Assignment registry unavailable. No empty result is inferred.</p>}
    {state.status==='VERIFIED'&&<>
      <div className={styles.controls}>
        <button type="button" onClick={()=>setEditing(value=>!value)}
          disabled={busy||!positions.length}>{editing?'Close assignment draft':'Propose assignment'}</button>
        <span>{state.data.current.length} verified active graph assignments</span>
      </div>
      <p className={styles.boundary}>
        Legacy employee department labels and verified operating-entity links are not yet synchronized.
        This graph does not change admission, payroll or business-role access.
      </p>
      <div className={styles.planning} aria-label="Approved position utilization">
        <strong>Approved position utilization</strong>
        {planning.status==='PENDING'&&<p role="status">Verifying governed position capacity…</p>}
        {planning.status==='DENIED'&&<p role="status">Position utilization denied by EOS.</p>}
        {planning.status==='UNAVAILABLE'&&<p role="status">Utilization source unavailable; no vacancy or zero count inferred.</p>}
        {planning.status==='VERIFIED'&&<>
          <div className={styles.pageControls}>
            <span>{planning.data.total} approved position records · page {planningPage+1}</span>
            <button type="button" disabled={planningPage===0}
              onClick={()=>setPlanningPage(p=>Math.max(0,p-1))}>Previous positions</button>
            <button type="button" disabled={!planning.data.has_more}
              onClick={()=>setPlanningPage(p=>p+1)}>Next positions</button>
          </div>
          {planning.data.items.map(pos=><div className={styles.position} key={pos.position_id}>
            <span><strong>{pos.name}</strong> · {pos.department_id}</span>
            <span>{pos.governed_assignments}/{pos.approved_capacity} graph assignments
              {' · '}{pos.unfilled_graph_slots} unfilled slots
              {!pos.position_currently_effective?' · future-effective':''}</span>
          </div>)}
          <small>Graph slots are not funded requisitions or reconciled employee headcount.</small>
        </>}
      </div>
      {editing&&<form className={styles.form} aria-label="Governed assignment form" onSubmit={event=>{
        event.preventDefault();
        if(!form.employee_id||!form.position_id||!form.effective_from||form.reason.trim().length<5)return;
        void send(ROOT+'/proposals',{...form,reason:form.reason.trim()});
      }}>
        <label>Find authorized employee
          <input type="search" value={filter} placeholder="Search name or employee ID (2+ characters)"
            onChange={event=>{setPage(0);setFilter(event.target.value);}}/>
        </label>
        <div className={styles.pageControls}>
          <span>{directory.status==='VERIFIED'?directory.total+' employees matching':'Employee source '+directory.status.toLowerCase()}</span>
          <button type="button" onClick={()=>setPage(p=>Math.max(0,p-1))}
            disabled={page===0||directory.status!=='VERIFIED'}>Previous</button>
          <button type="button" onClick={()=>setPage(p=>p+1)}
            disabled={directory.status!=='VERIFIED'||(page+1)*50>=directory.total}>Next</button>
        </div>
        <label>Employee
          <select required value={form.employee_id} onChange={event=>setForm(f=>({...f,employee_id:event.target.value}))}
            disabled={directory.status!=='VERIFIED'}>
            <option value="">Choose verified employee</option>
            {directory.items.map(person=><option key={person.employeeId} value={person.employeeId}>
              {person.displayName || person.employeeId} · {person.employeeId}
            </option>)}
          </select>
        </label>
        <label>Approved position
          <select required value={form.position_id} onChange={event=>setForm(f=>({...f,position_id:event.target.value}))}>
            <option value="">Choose approved position</option>
            {positions.map(pos=><option key={pos.record_id} value={pos.record_id}>
              {pos.name} · {pos.department_id} · capacity {pos.capacity}
            </option>)}
          </select>
        </label>
        <label>Effective from
          <input type="date" required value={form.effective_from}
            onChange={event=>setForm(f=>({...f,effective_from:event.target.value}))}/>
        </label>
        <label>Reason for assignment or move
          <textarea required minLength={5} maxLength={2000} value={form.reason}
            onChange={event=>setForm(f=>({...f,reason:event.target.value}))}/>
        </label>
        <button type="submit" disabled={busy||directory.status!=='VERIFIED'||
          !form.employee_id||!form.position_id||!form.effective_from||form.reason.trim().length<5}>
          Save assignment draft
        </button>
      </form>}
      <div className={styles.list}>
        {state.data.proposals.map(item=><div className={styles.row} key={item.proposal_id}>
          <div><strong>{item.employee_id} → {item.position_id}</strong>
            <p>{item.status} · {item.department_id} · effective {item.effective_from}</p>
          </div>
          {item.status==='DRAFT'&&item.current_principal_is_maker&&
            <button type="button" disabled={busy} onClick={()=>void send(
              ROOT+'/proposals/'+encodeURIComponent(item.proposal_id)+'/submit',
              {expected_revision:item.revision})}>Submit for review</button>}
          {item.status==='SUBMITTED'&&!item.current_principal_is_maker&&<div className={styles.actions}>
            <input aria-label={'Decision reason '+item.proposal_id} placeholder="Independent checker reason"
              value={reviewReasons[item.proposal_id]||''}
              onChange={event=>setReviewReasons(previous=>({...previous,[item.proposal_id]:event.target.value}))}/>
            {['APPROVE','REJECT'].map(decision=><button type="button" key={decision}
              disabled={busy||(reviewReasons[item.proposal_id]||'').trim().length<5}
              onClick={()=>void send(ROOT+'/proposals/'+encodeURIComponent(item.proposal_id)+'/decision',
                {expected_revision:item.revision,decision,reason:reviewReasons[item.proposal_id].trim()})}>
              {decision==='APPROVE'?'Approve':'Reject'}</button>)}
          </div>}
        </div>)}
        {!state.data.proposals.length&&<p>No assignment proposals yet in this verified source.</p>}
        {state.data.current.map(a=><div key={a.employee_id} className={styles.row}>
          <div><strong>{a.employee_id} → {a.position_id}</strong>
            <p>{a.department_id} · revision {a.revision} · effective {a.effective_from}</p>
          </div>
          <button type="button" disabled={busy}
            onClick={()=>void inspectHistory(a.employee_id)}>History</button>
        </div>)}
      </div>
      {history&&<div className={styles.history}>
        <strong>{history.employee_id} · assignment history</strong>
        {history.items.map(row=><p key={row.revision}>Revision {row.revision} ·
          {' '}{row.position_id} → {row.department_id} · effective {row.effective_from}</p>)}
      </div>}
    </>}
    {notice&&<p className={styles.notice} role="status">{notice}</p>}
  </section>;
}
/**
 * ARTIFACT: client/src/components/hr/OrganizationAssignmentWorkspace.jsx
 * VERSION: v1.0.0-M03-HR03-EMPLOYEE-POSITION-ASSIGNMENT-CLIENT
 * TENANT POSTURE: Current authenticated tenant and principal; no scope fallback.
 * AUTHORITY BOUNDARY: Client sends proposed commands; Python EOS decides.
 * FAIL-CLOSED POSTURE: Only verified source responses can display durable success.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
