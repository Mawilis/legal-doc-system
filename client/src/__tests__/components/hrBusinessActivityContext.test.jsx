/**
 * TITLE: WILSY OS Governed Business Context Client Regression
 * VERSION: v1.0.0-M03-HR03-BUSINESS-CONTEXT-UI-CERT
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Exact-tenant approved context, denial and draft-only client behavior.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/hrBusinessActivityContext.test.jsx
 * COLLABORATION / OWNERSHIP: WILSY OS People engineering
 * CERTIFICATION / UPDATE DATE: 2026-11-28
 * CHANGELOG: v1.0.0-M03-HR03-BUSINESS-CONTEXT-UI-CERT adds synthetic nonproduction tests.
 * COMPLIANCE: POPIA section 19 / GDPR Article 32 / SOC 2 CC7.2 technical boundaries.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant and activity references only.
 * TENANT BOUNDARY: No cross-tenant result admitted or inferred.
 * AUTHORITY BOUNDARY: EOS-only mutations, never browser IAM.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import BusinessActivityContextWorkspace from '../../components/hr/BusinessActivityContextWorkspace';

const api = vi.hoisted(() => ({get:vi.fn(),post:vi.fn()}));
vi.mock('../../services/api',()=>({default:api}));

const response = (tenant,status='APPROVED') => ({data:{
  schema:'WILSY-HR-BUSINESS-ACTIVITY-CONTEXT/V1',
  source:'EOS_APPROVED_TENANT_BUSINESS_ACTIVITIES',
  tenant_id:tenant, status,
  activity_ids:status==='APPROVED' ? ['legal','technology'] : [],
  revision:status==='APPROVED'?2:0, proposals:[],
  operating_entities:[],entity_status:'ENTITY_SOURCE_NOT_CONNECTED',
  external_business_classification_verified:false,
}});

beforeEach(()=>{api.get.mockReset();api.post.mockReset();});
afterEach(()=>cleanup());

describe('governed business activity context',()=>{
  it('uses approved own-tenant activities and never invents a legal entity',async()=>{
    api.get.mockResolvedValue(response('TENANT-A'));
    const onApproved=vi.fn();
    render(<BusinessActivityContextWorkspace tenantId="TENANT-A" scopeKey="TENANT-A/P-A/S-1" onApproved={onApproved}/>);
    expect(await screen.findByText(/Law firm & legal services/)).toBeInTheDocument();
    expect(screen.getByText(/Verified operating-entity linkage is not yet connected/)).toBeInTheDocument();
    expect(onApproved).toHaveBeenCalledWith(['legal','technology']);
    expect(api.post).not.toHaveBeenCalled();
  });

  it('preserves 403 denial, without a privileged fallback or false sector',async()=>{
    api.get.mockRejectedValue({response:{status:403}});
    const onApproved=vi.fn();
    render(<BusinessActivityContextWorkspace tenantId="TENANT-A" scopeKey="TENANT-A/P-A/S-1" onApproved={onApproved}/>);
    expect(await screen.findByRole('alert')).toHaveTextContent('denied');
    expect(onApproved).toHaveBeenCalledWith([]);
    expect(api.post).not.toHaveBeenCalled();
  });

  it('keeps activity selection local until the operator explicitly saves a proposal',async()=>{
    api.get.mockResolvedValue(response('TENANT-A','UNCONFIGURED'));
    render(<BusinessActivityContextWorkspace tenantId="TENANT-A" scopeKey="TENANT-A/P-A/S-1"/>);
    fireEvent.click(await screen.findByRole('button',{name:'Manage activities'}));
    fireEvent.click(screen.getByRole('checkbox',{name:'Medical practice & clinic'}));
    fireEvent.change(screen.getByRole('textbox',{name:'Business justification'}),{
      target:{value:'We deliver clinical services and patient care'},
    });
    expect(api.post).not.toHaveBeenCalled();
    expect(screen.getByRole('button',{name:'Save activity proposal'})).toBeEnabled();
  });

  it('rejects a foreign-tenant context instead of personalizing from it',async()=>{
    api.get.mockResolvedValue(response('TENANT-FOREIGN'));
    render(<BusinessActivityContextWorkspace tenantId="TENANT-A" scopeKey="TENANT-A/P-A/S-1"/>);
    expect(await screen.findByText(/could not be verified/)).toBeInTheDocument();
    expect(screen.queryByText(/Law firm & legal services/)).not.toBeInTheDocument();
  });
});

/**
 * ARTIFACT: client/src/__tests__/components/hrBusinessActivityContext.test.jsx
 * VERSION: v1.0.0-M03-HR03-BUSINESS-CONTEXT-UI-CERT
 * AUTHORITY BOUNDARY: Tests only; no grant or client-created profile authority.
 * TENANT POSTURE: Exact synthetic tenant, foreign read rejected.
 * FAIL-CLOSED POSTURE: Denied and invalid payloads are not treated as approved.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
