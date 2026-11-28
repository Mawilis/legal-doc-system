/**
 * TITLE: WILSY OS Governed Department Lifecycle Client Certificate
 * VERSION: v1.0.0-M03-HR03-DEPARTMENT-CLIENT-CERT
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Synthetic authenticated lifecycle, independent checker and staffing reconciliation UI.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/hrOrganizationLifecycleWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: WILSY OS HR Organization engineering
 * CERTIFICATION / UPDATE DATE: 2026-11-28
 * CHANGELOG: v1.0.0-M03-HR03-DEPARTMENT-CLIENT-CERT establishes readback, denial and historical evidence tests.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 test boundaries.
 * SECURITY / PRIVACY POSTURE: Synthetic identifiers and aggregate counts only.
 * TENANT BOUNDARY: All read results bind one synthetic authenticated tenant.
 * AUTHORITY BOUNDARY: All commands remain source-enforced, no Owner fallback.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import OrganizationLifecycleWorkspace from '../../components/hr/OrganizationLifecycleWorkspace';

const api = vi.hoisted(() => ({get:vi.fn(),post:vi.fn()}));
vi.mock('../../services/api',()=>({default:api}));

const tenant='TENANT-SYNTHETIC-A';
const structure={items:[{
  kind:'DEPARTMENT',record_id:'DEP-OPS',name:'Operations',
  status:'APPROVED',revision:3,effective_from:'2026-01-01',
}]};
const changes=(items=[])=>({data:{
  schema:'WILSY-HR-ORGANIZATION-CHANGES/V1',
  tenant_id:tenant,source:'EOS_HR_ORGANIZATION_CHANGES',
  count:items.length,items,
}});
const productivity=()=>({data:{
  schema:'WILSY-HR-ORGANIZATION-PRODUCTIVITY/V1',
  tenant_id:tenant,source:'EOS_ORGANIZATION_CHANGE_EVENTS',
  change_drafts:0,approved_changes:0,rejected_changes:0,
  client_observation_sample:0,client_observed:{},
  mean_draft_to_decision_seconds:null,
}});
const staffing=()=>({data:{
  schema:'WILSY-HR-STAFFING-RECONCILIATION/V1',
  tenant_id:tenant,source:'EOS_LEGACY_EMPLOYEE_DEPARTMENT_LABELS',
  reconciliation_kind:'READ_ONLY_OBSERVATION',
  unmatched_active_employees:2,ambiguous_active_employees:1,
  candidate_matches:[{department_id:'DEP-OPS',employee_count:5,
    relationship:'LABEL_CANDIDATE_NOT_AUTHORIZED_ASSIGNMENT'}],
  source_total_active:8,employee_assignment_linkage_certified:false,
  retirement_approval_permitted:false,
}});
const impact=()=>({data:{
  schema:'WILSY-HR-ORGANIZATION-IMPACT/V1',
  tenant_id:tenant,record_id:'DEP-OPS',dependent_positions:['POS-ONE'],
  dependent_departments:[],retirement_blocked:true,
  staffing_dependency_status:'NOT_CERTIFIED',
}});
const history=()=>({data:{
  schema:'WILSY-HR-ORGANIZATION-HISTORY/V1',
  tenant_id:tenant,record_id:'DEP-OPS',count:1,items:[
    {revision:3,name:'Operations',status:'APPROVED',
      effective_from:'2026-01-01'},
  ],
}});
function defaultGet(path) {
  if(path.endsWith('/changes'))return Promise.resolve(changes());
  if(path.endsWith('/productivity'))return Promise.resolve(productivity());
  if(path.endsWith('/staffing-reconciliation'))return Promise.resolve(staffing());
  if(path.endsWith('/DEP-OPS/impact'))return Promise.resolve(impact());
  if(path.endsWith('/DEP-OPS/history'))return Promise.resolve(history());
  if(path.endsWith('/DEP-OPS/as-of'))return Promise.resolve({data:{
    schema:'WILSY-HR-ORGANIZATION-AS-OF/V1',
    tenant_id:tenant,record_id:'DEP-OPS',as_of:'2026-11-01',
    record:{name:'Operations',status:'APPROVED',revision:3},
  }});
  return Promise.reject({response:{status:404}});
}
beforeEach(()=>{api.get.mockReset();api.post.mockReset();api.get.mockImplementation(defaultGet);});
afterEach(()=>cleanup());
const open=()=>render(<OrganizationLifecycleWorkspace tenantId={tenant}
  scopeKey="TENANT-SYNTHETIC-A/PRINCIPAL-ONE/SESSION-1"
  structure={structure}/>);

describe('governed department change workspace',()=>{
  it('shows source readback and never upgrades legacy employee labels to assignments',async()=>{
    open();
    expect(await screen.findByText('0 verified change proposals')).toBeInTheDocument();
    expect(await screen.findByText(/8 active employee records/)).toBeInTheDocument();
    expect(screen.getByText(/These are observations, not canonical employee assignments/)).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
  it('distinguishes denied staffing read from authorized change operations',async()=>{
    api.get.mockImplementation(path=>
      path.endsWith('/staffing-reconciliation')
        ? Promise.reject({response:{status:403}}) : defaultGet(path));
    open();
    expect(await screen.findByText('0 verified change proposals')).toBeInTheDocument();
    expect(await screen.findByText(/Employee source permission denied/)).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
  it('requires a second checker and reason rather than showing maker approval',async()=>{
    api.get.mockImplementation(path=>path.endsWith('/changes')
      ? Promise.resolve(changes([{
          change_id:'CHANGE-ONE',record_id:'DEP-OPS',
          change_type:'AMEND',status:'SUBMITTED',revision:2,
          effective_from:'2026-12-01',current_principal_is_maker:true,
        }])) : defaultGet(path));
    open();
    expect(await screen.findByText('1 verified change proposals')).toBeInTheDocument();
    expect(screen.queryByRole('button',{name:'Approve'})).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
  it('inspects historical department evidence without issuing a mutation',async()=>{
    open();
    const chooser=await screen.findByLabelText('Inspect a department');
    fireEvent.change(chooser,{target:{value:'DEP-OPS'}});
    expect(await screen.findByText(/Revision 3 · Operations · APPROVED/)).toBeInTheDocument();
    expect(await screen.findByText(/Retirement is blocked/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('As of date'),{
      target:{value:'2026-11-01'},
    });
    fireEvent.click(screen.getByRole('button',{name:'Inspect verified snapshot'}));
    expect(await screen.findByText(/On 2026-11-01: Operations/)).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
  it('denied change queue remains unavailable, never a fabricated empty list',async()=>{
    api.get.mockImplementation(path=>path.endsWith('/changes')
      ? Promise.reject({response:{status:403}}) : defaultGet(path));
    open();
    expect(await screen.findByRole('alert')).toHaveTextContent('denied');
    expect(screen.queryByText('0 verified change proposals')).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: client/src/__tests__/components/hrOrganizationLifecycleWorkspace.test.jsx
 * VERSION: v1.0.0-M03-HR03-DEPARTMENT-CLIENT-CERT
 * AUTHORITY BOUNDARY: Client test only; EOS independently checks commands.
 * TENANT POSTURE: Synthetic tenant binds every accepted response.
 * FAIL-CLOSED POSTURE: Denied and unverified sources never claim a saved change.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
