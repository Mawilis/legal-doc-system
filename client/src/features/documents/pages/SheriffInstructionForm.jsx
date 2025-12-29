import React from 'react';
import { Formik, Form, Field, ErrorMessage, useFormikContext } from 'formik';
import * as Yup from 'yup';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { apiPost } from '../../../services/http'; 
import AddressAutocomplete from '../../../components/AddressAutocomplete';

// --- STYLES ---
const PageLayout = styled.div`
  padding: 40px; background: #f0f4f8; font-family: 'Inter', sans-serif; min-height: 100vh;
  display: grid; grid-template-columns: 1fr 380px; gap: 30px;
`;
const Card = styled.div` background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); padding: 30px; margin-bottom: 24px; border: 1px solid #e1e4e8; `;
const SectionTitle = styled.h3` font-size: 0.95rem; font-weight: 700; color: #1e293b; margin: 0 0 20px 0; padding-bottom: 10px; border-bottom: 1px solid #eee; text-transform: uppercase; `;
const Grid2 = styled.div` display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 15px; `;
const Grid3 = styled.div` display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 15px; `;
const Label = styled.label` display: block; font-size: 0.85rem; color: #475569; margin-bottom: 6px; font-weight: 600; `;
const Input = styled(Field)` width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.95rem; background:#fff; &:focus { outline: none; border-color: #2563eb; } `;
const Select = styled(Field)` width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.95rem; background: #fff; `;
const ErrorText = styled(ErrorMessage)` color: #ef4444; font-size: 0.75rem; margin-top: 4px; display: block; `;
const ButtonPrimary = styled.button` width: 100%; padding: 16px; background: #0f172a; color: #fff; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; margin-top:10px; font-size:1rem; &:disabled { opacity: 0.7; cursor: not-allowed; } `;
const StatRow = styled.div` display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed #e2e8f0; font-size: 0.9rem; color: #334155; `;

// --- DATA CONSTANTS ---
const CLASSIFICATIONS = ['LITIGATION', 'FAMILY', 'COMMERCIAL', 'PROPERTY', 'PRE-LITIGATION'];
const URGENCY = ['normal', 'urgent', 'high'];

const SERVICE_TYPES = [
  { id: 'service_of_summons', label: '1. Service of Summons', base: 180, plan: '3 Attempts / 7 Days' },
  { id: 'urgent_service_rule_6_12', label: '2. Urgent Service (Rule 6(12))', base: 450, plan: 'Immediate / 24 Hours' },
  { id: 'writ_execution_movables', label: '3. Writ of Execution (Movables)', base: 950, plan: 'Attachment & Inventory' },
  { id: 'writ_execution_immovables', label: '4. Writ of Execution (Immovables)', base: 1200, plan: 'Attachment & Notices' },
  { id: 'ejectment_eviction', label: '5. Ejectment / Eviction', base: 1500, plan: 'SAPS Coordination Required' },
  { id: 'service_of_interdict', label: '6. Service of Interdict', base: 400, plan: 'Personal Service Mandatory' },
  { id: 'garnishee_order', label: '7. Garnishee Order', base: 350, plan: 'Service on Employer' },
  { id: 'bank_attachment', label: '8. Bank Attachment', base: 500, plan: 'Service on Bank HQ' },
  { id: 'subpoena', label: '9. Subpoena', base: 250, plan: 'Personal Service Preferred' },
  { id: 'substituted_service', label: '10. Substituted Service', base: 220, plan: 'Via Email/Publication' },
  { id: 'corporate_service', label: '11. Corporate Service', base: 280, plan: 'Registered Office (CIPC)' },
  { id: 'personal_service_strict', label: '12. Personal Service (Strict)', base: 300, plan: 'Hand Delivery Only' }
];

// --- PRICING ALGORITHM ---
const calculatePricing = (values) => {
  const typeDef = SERVICE_TYPES.find(t => t.id === values.serviceType) || SERVICE_TYPES[0];
  let total = typeDef.base;
  
  // Multipliers
  if (values.urgency === 'urgent') total *= 1.5; 
  if (values.urgency === 'high') total *= 2.0;   
  if (values.afterHours) total *= 1.25;

  // Distance Band
  const dist = parseFloat(values.distanceKm) || 0;
  const travel = dist * 6.50; 
  total += travel;

  // Extras
  if (values.locksmith) total += 450;
  if (values.security) total += 400;
  if (values.transport) total += 300;

  const vat = total * 0.15;
  return { base: typeDef.base, travel, vat, total: total + vat };
};

// --- REACTIVE SIDEBAR COMPONENT ---
const CostEstimator = () => {
  const { values, handleChange } = useFormikContext(); // HOOK INTO STATE INSTANTLY
  const financials = calculatePricing(values);

  return (
    <Card style={{position:'sticky', top:'20px'}}>
        <SectionTitle>💰 Live Invoice</SectionTitle>
        
        <div style={{marginBottom:'25px'}}>
            <Label>Travel Distance: {values.distanceKm} km</Label>
            <input 
                type="range" min="0" max="100" 
                name="distanceKm"
                value={values.distanceKm} 
                onChange={handleChange}
                style={{width:'100%', accentColor:'#0f172a'}} 
            />
        </div>

        <Label>Urgency Level</Label>
        <Select as="select" name="urgency" style={{marginBottom:'20px'}}>
            {URGENCY.map(u => <option key={u} value={u}>{u.toUpperCase()}</option>)}
        </Select>

        <div style={{background:'#f8fafc', padding:'15px', borderRadius:'8px', border:'1px solid #e2e8f0'}}>
            <StatRow><span>Base Tariff</span><span>R {financials.base.toFixed(2)}</span></StatRow>
            <StatRow><span>Travel Fee</span><span>R {financials.travel.toFixed(2)}</span></StatRow>
            <StatRow><span>VAT (15%)</span><span>R {financials.vat.toFixed(2)}</span></StatRow>
            <StatRow style={{borderTop:'2px solid #000', marginTop:'10px', paddingTop:'10px'}}>
                <span style={{fontWeight:'800'}}>TOTAL</span>
                <span style={{color:'#2563eb', fontWeight:'800', fontSize:'1.2rem'}}>R {financials.total.toFixed(2)}</span>
            </StatRow>
        </div>
    </Card>
  );
};

export default function SheriffInstructionForm() {
  const navigate = useNavigate();

  const initialValues = {
    title: '', caseNumber: '', court: '', classification: 'LITIGATION',
    plaintiff: '', defendant: '',
    serviceType: 'service_of_summons',
    serviceAddress: '', street: '', city: '', province: '', postalCode: '',
    urgency: 'normal',
    distanceKm: 15,
    afterHours: false, locksmith: false, security: false, transport: false,
    documentCode: `SHF-${Date.now().toString().slice(-6)}`,
    
    // Dynamic Fields
    urgentReason: '', ruleReference: '', deadlineAt: '',
    orderRef: '', securityPlan: '', warehouseProvider: '',
    courtOrderAuthorizing: '', mediaChannels: [],
    registeredOfficeAddress: '', cipcVerified: false
  };

  const Schema = Yup.object().shape({
    title: Yup.string().required('Title is required'),
    caseNumber: Yup.string().required('Case Number is required'),
    court: Yup.string().required('Court is required'),
    street: Yup.string().required('Address is required'),
    
    // DYNAMIC VALIDATION RULES
    urgentReason: Yup.string().when('urgency', {
        is: (val) => val === 'urgent' || val === 'high',
        then: () => Yup.string().required('Urgency Reason is MANDATORY for Rule 6(12)')
    }),
    securityPlan: Yup.string().when('serviceType', {
        is: (val) => val === 'writ_execution_movables' || val === 'ejectment_eviction',
        then: () => Yup.string().required('Security Plan is required for this execution type')
    })
  });

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      const typeDef = SERVICE_TYPES.find(t => t.id === values.serviceType);
      const financials = calculatePricing(values);

      const payload = {
        ...values,
        attemptPlan: { 
            window: typeDef.plan, 
            minAttempts: values.urgency === 'normal' ? 3 : 1 
        },
        pricingPreview: financials,
        serviceAddress: `${values.street}, ${values.city}, ${values.province}`,
        status: 'Pending Dispatch'
      };

      await apiPost('/dispatch-instructions', payload);
      navigate('/documents');
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Formik initialValues={initialValues} validationSchema={Schema} onSubmit={handleSubmit}>
      {({ values, setFieldValue, handleChange, isSubmitting }) => {
        const currentType = SERVICE_TYPES.find(t => t.id === values.serviceType) || SERVICE_TYPES[0];

        return (
          <Form>
            <PageLayout>
              {/* LEFT COLUMN: FORM */}
              <div>
                <div style={{marginBottom:'30px'}}>
                  <div style={{background:'#0f172a', color:'#fff', padding:'5px 10px', borderRadius:'4px', display:'inline-block', fontSize:'0.75rem', fontWeight:'bold', marginBottom:'10px'}}>
                      SHERIFF OPERATIONS OS v2.0
                  </div>
                  <h1 style={{fontSize:'2rem', fontWeight:'800', color:'#0f172a', margin:0}}>New Dispatch Instruction</h1>
                </div>

                <Card>
                  <SectionTitle>⚖️ Case Identity</SectionTitle>
                  <Grid2>
                    <div><Label>Instruction Title</Label><Input name="title" /><ErrorText name="title" component="div"/></div>
                    <div><Label>Code</Label><Input name="documentCode" disabled style={{background:'#f1f5f9'}} /></div>
                  </Grid2>
                  <Grid3>
                    <div><Label>Case Number</Label><Input name="caseNumber" /><ErrorText name="caseNumber" component="div"/></div>
                    <div><Label>Court</Label><Input name="court" /><ErrorText name="court" component="div"/></div>
                    <div><Label>Plaintiff</Label><Input name="plaintiff" /></div>
                  </Grid3>
                </Card>

                <Card>
                  <SectionTitle>🚚 Logistics</SectionTitle>
                  <Grid2>
                    <div>
                        <Label>Service Type</Label>
                        <Select as="select" name="serviceType">
                            {SERVICE_TYPES.map(t=><option key={t.id} value={t.id}>{t.label}</option>)}
                        </Select>
                        <div style={{fontSize:'0.8rem', color:'#2563eb', marginTop:'5px', fontWeight:'600'}}>
                            Strategy: {currentType.plan}
                        </div>
                    </div>
                    <div>
                        <Label>Address</Label>
                        <AddressAutocomplete 
                            name="street" 
                            value={values.street} 
                            onChange={handleChange} 
                            onSelect={place => { 
                                setFieldValue('street', place.street); 
                                setFieldValue('city', place.city); 
                                setFieldValue('province', place.province); 
                            }} 
                        />
                        <ErrorText name="street" component="div"/>
                    </div>
                  </Grid2>
                  
                  <div style={{background:'#f8fafc', padding:'15px', borderRadius:'8px', marginTop:'20px'}}>
                      <Label style={{marginBottom:'10px'}}>Risk & Access</Label>
                      <Grid2>
                          <div style={{display:'flex', gap:'15px', alignItems:'center'}}>
                              <label><Field type="checkbox" name="afterHours" /> After Hours</label>
                              <label><Field type="checkbox" name="locksmith" /> Locksmith</label>
                              <label><Field type="checkbox" name="security" /> Security</label>
                          </div>
                      </Grid2>
                  </div>

                  {/* DYNAMIC FIELDS: URGENT */}
                  {(values.urgency === 'urgent' || values.urgency === 'high') && (
                      <div style={{marginTop:'20px', borderLeft:'4px solid #ef4444', paddingLeft:'15px'}}>
                          <Label style={{color:'#ef4444'}}>Urgency Justification (Rule 6(12))</Label>
                          <Grid2>
                              <div><Input name="urgentReason" placeholder="Reason..." /><ErrorText name="urgentReason" component="div"/></div>
                              <div><Input name="ruleReference" placeholder="e.g. Rule 6(12)(a)" /></div>
                          </Grid2>
                      </div>
                  )}

                  {/* DYNAMIC FIELDS: WRIT / EVICTION */}
                  {(values.serviceType === 'writ_execution_movables' || values.serviceType === 'ejectment_eviction') && (
                      <div style={{marginTop:'20px', borderLeft:'4px solid #f59e0b', paddingLeft:'15px'}}>
                          <Label style={{color:'#d97706'}}>Execution Logistics</Label>
                          <Grid2>
                              <div><Input name="securityPlan" placeholder="Security Provider..." /><ErrorText name="securityPlan" component="div"/></div>
                              <div><Input name="warehouseProvider" placeholder="Warehouse..." /></div>
                          </Grid2>
                      </div>
                  )}
                </Card>

                <ButtonPrimary type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'DISPATCHING...' : 'GENERATE INSTRUCTION'}
                </ButtonPrimary>
              </div>

              {/* RIGHT COLUMN: REACTIVE SIDEBAR */}
              <CostEstimator />
            </PageLayout>
          </Form>
        );
      }}
    </Formik>
  );
}
