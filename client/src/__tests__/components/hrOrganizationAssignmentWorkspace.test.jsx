/**
 * TITLE: WILSY OS HR03 Governed Assignment Client Regression
 * VERSION: v1.0.0-M03-HR03-ASSIGNMENT-CLIENT-CERT
 * AUTHORITY: WILSY OS People source verification.
 * EPITOME: Check tenant-bound assignment state, authorized employees and checker UI.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/hrOrganizationAssignmentWorkspace.test.jsx
 * COLLABORATION / OWNERSHIP: WILSY OS HR engineering.
 * CERTIFICATION / UPDATE DATE: 2026-11-28
 * CHANGELOG: v1.0.0 verifies source denial, employee select and checker presentation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; WCAG 2.2 semantic testing.
 * SECURITY / PRIVACY POSTURE: Synthetic employer and employee records only.
 * TENANT BOUNDARY: Exact authenticated tenant, no fallback.
 * AUTHORITY BOUNDARY: Client does not grant organization or relation authority.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS only.
 */
import React from 'react';
import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import OrganizationAssignmentWorkspace from '../../components/hr/OrganizationAssignmentWorkspace.jsx';

const api=vi.hoisted(()=>({get:vi.fn(),post:vi.fn()}));
vi.mock('../../services/api',()=>({default:api}));
const tenant='TENANT-SYNTHETIC-A';
const structure={items:[{
  kind:'POSITION',status:'APPROVED',record_id:'POS-LAB',
  name:'Laboratory Technician',department_id:'DEP-LAB',capacity:2,
}]};
const source=(proposals=[],current=[])=>({data:{
  schema:'WILSY-HR-GOVERNED-ASSIGNMENTS/V1',tenant_id:tenant,
  source:'EOS_HR_ASSIGNMENT_REGISTRY',
  proposals,current,legacy_employee_fields_synchronized:false,
  verified_operating_entity_connected:false,
}});
const directory=()=>({data:{
  source:'AUTHORISED_HR_EMPLOYEE_REGISTRY',total:1,
  offset:0,limit:50,items:[{employeeId:'EMP-ONE',displayName:'Synthetic Employee'}],
}});
const start=()=>render(<OrganizationAssignmentWorkspace tenantId={tenant}
  scopeKey={tenant+'/HR-MANAGER/SESSION-ONE'} structure={structure}/>);

beforeEach(()=>{
  api.get.mockReset();api.post.mockReset();
  api.get.mockImplementation(path=>{
    if(path==='/hr/workforce/assignments')return Promise.resolve(source());
    if(path==='/hr/workforce')return Promise.resolve(directory());
    return Promise.reject({response:{status:404}});
  });
});
afterEach(()=>cleanup());

describe('governed employee position assignments',()=>{
  it('loads a source-owned empty registry instead of inventing staffing data',async()=>{
    start();
    expect(await screen.findByText('0 verified active graph assignments')).toBeInTheDocument();
    expect(screen.getByText(/Legacy employee department labels/)).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
  it('fails closed on a denied assignment permission',async()=>{
    api.get.mockRejectedValue({response:{status:403}});
    start();
    expect(await screen.findByRole('alert')).toHaveTextContent('denied');
    expect(screen.queryByRole('button',{name:'Propose assignment'})).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
  it('chooses existing source employees and approved positions without a write',async()=>{
    start();
    fireEvent.click(await screen.findByRole('button',{name:'Propose assignment'}));
    const employee=await screen.findByRole('option',{name:'Synthetic Employee · EMP-ONE'});
    expect(employee).toBeInTheDocument();
    expect(screen.getByRole('option',{name:/Laboratory Technician · DEP-LAB/})).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Employee'),{target:{value:'EMP-ONE'}});
    fireEvent.change(screen.getByLabelText('Approved position'),{target:{value:'POS-LAB'}});
    expect(screen.getByLabelText('Employee')).toHaveValue('EMP-ONE');
    expect(api.post).not.toHaveBeenCalled();
  });
  it('does not present independent decision controls to a maker',async()=>{
    api.get.mockImplementation(path=>{
      if(path==='/hr/workforce/assignments')return Promise.resolve(source([{
        proposal_id:'PROP-ONE',employee_id:'EMP-ONE',position_id:'POS-LAB',
        department_id:'DEP-LAB',status:'SUBMITTED',revision:2,
        current_principal_is_maker:true,effective_from:'2026-11-28',
      }]));
      return Promise.resolve(directory());
    });
    start();
    expect(await screen.findByText('EMP-ONE → POS-LAB')).toBeInTheDocument();
    expect(screen.queryByRole('button',{name:'Approve'})).not.toBeInTheDocument();
  });
  it('rejects cross-tenant assignment readback even when HTTP succeeds',async()=>{
    api.get.mockImplementation(path=>path==='/hr/workforce/assignments'
      ? Promise.resolve({data:{...source().data,tenant_id:'TENANT-FOREIGN'}})
      : Promise.resolve(directory()));
    start();
    expect(await screen.findByText(/Assignment registry unavailable/)).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
});
/**
 * ARTIFACT: client/src/__tests__/components/hrOrganizationAssignmentWorkspace.test.jsx
 * VERSION: v1.0.0-M03-HR03-ASSIGNMENT-CLIENT-CERT
 * TENANT POSTURE: All samples are synthetic and exact tenant scoped.
 * AUTHORITY BOUNDARY: No simulated IAM grant or employee admission.
 * FAIL-CLOSED POSTURE: Unverified reads cannot claim success.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
