import React, { useMemo, useState } from 'react';
import styled from 'styled-components';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useNavigate } from 'react-router-dom';
import { apiPost } from '../../../services/http';
import { SA_COURTS } from '../../../data/saCourts';
import AddressAutocomplete from '../../../components/AddressAutocomplete';

// --- STYLES ---
const Page = styled.div` display: grid; grid-template-columns: 1fr 360px; gap: 24px; padding: 40px; background: #f7f9fc; font-family: 'Inter', sans-serif; min-height: 100vh; `;
const Card = styled.div` background: #fff; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); padding: 32px; border: 1px solid #f3f4f6; `;
const Title = styled.h1` font-size: 1.5rem; margin: 0 0 8px 0; color: #111827; font-weight: 700; `;
const SubTitle = styled.h2` font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin: 24px 0 16px 0; color: #6b7280; font-weight: 600; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; `;
const Grid2 = styled.div` display: grid; grid-template-columns: 1fr 1fr; gap: 20px; `;
const Grid3 = styled.div` display: grid; grid-template-columns: 1.4fr 0.8fr 0.8fr; gap: 20px; `;
const Label = styled.label` display: block; font-size: 0.875rem; color: #374151; margin-bottom: 6px; font-weight: 500; `;
const Input = styled(Field)` width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.95rem; background: #fff; &:focus { outline: none; border-color: #2563eb; ring: 2px solid rgba(37,99,235,0.1); } &:disabled { background: #f3f4f6; color: #6b7280; cursor: not-allowed; } `;
const TextArea = styled(Field)` width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.95rem; background: #fff; min-height: 80px; font-family: inherit; &:focus { outline: none; border-color: #2563eb; ring: 2px solid rgba(37,99,235,0.1); } `;
const Select = styled(Field)` width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; font-size: 0.95rem; `;
const ErrorText = styled(ErrorMessage)` color: #dc2626; font-size: 0.75rem; margin-top: 4px; `;
const ButtonPrimary = styled.button` width: 100%; padding: 14px; border: none; border-radius: 8px; background: #2563eb; color: #fff; font-weight: 600; font-size: 0.95rem; cursor: pointer; margin-top: 24px; transition: background 0.2s; &:hover { background: #1d4ed8; } &:disabled { background: #9ca3af; } `;
const Stat = styled.div` display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed #e5e7eb; font-size: 0.9rem; color: #4b5563; &:last-child { border-bottom: none; font-weight: 700; color: #111827; font-size: 1rem; } `;
const SearchList = styled.ul` list-style: none; padding: 0; margin: 4px 0 0; border: 1px solid #e5e7eb; border-radius: 6px; max-height: 200px; overflow-y: auto; background: white; position: absolute; width: 100%; z-index: 50; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); li { padding: 8px 12px; cursor: pointer; &:hover { background: #f9fafb; color: #2563eb; } } `;
const Row = styled.div` margin-bottom: 16px; position: relative; `;

// --- LOGIC ---
const getContextConfig = (type) => {
  const normalized = (type || '').toLowerCase();
  
  if (normalized.includes('divorce') || normalized.includes('family')) {
    return { partyALabel: 'Plaintiff (Spouse)', partyBLabel: 'Defendant (Spouse)', idLabel: 'ID / Passport Number', idPlaceholder: '13-digit SA ID or Passport' };
  }
  if (normalized.includes('commercial') || normalized.includes('company')) {
    return { partyALabel: 'Applicant (Entity)', partyBLabel: 'Respondent (Entity)', idLabel: 'Registration Number', idPlaceholder: 'e.g. 2023/123456/07' };
  }
  return { partyALabel: 'Plaintiff / Applicant', partyBLabel: 'Defendant / Respondent', idLabel: 'ID / Reg Number', idPlaceholder: 'ID or Company Reg No' };
};

const VAT_RATE = 0.15;

const UniversalLegalForm = ({ type = 'general', config }) => {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState(null);
  const context = getContextConfig(config.classification);
  
  const [courtSearch, setCourtSearch] = useState('');
  const [showCourts, setShowCourts] = useState(false);
  const filteredCourts = SA_COURTS.filter(c => c.name.toLowerCase().includes(courtSearch.toLowerCase()));

  const autoRef = useMemo(() => `MAT-${new Date().getFullYear()}-${Math.floor(Math.random() * 10000)}`, []);
  const autoCode = useMemo(() => `${config.classification.substring(0,3)}-${Date.now().toString().slice(-6)}`, [config]);

  const initialValues = {
    classification: config.classification,
    caseNumber: '',
    fileRef: autoRef,
    courtName: '',
    primaryParty: '',
    primaryId: '',
    opposingParty: '',
    opposingId: '',
    street: '',
    city: '',
    province: '',
    postalCode: '',
    baseTariff: config.baseFee || 1500,
    title: '',
    documentCode: autoCode,
    marriageType: 'ANC_WITH',
    childrenCount: 0,
    claimAmount: '',
    causeOfAction: '',
    urgencyReason: ''
  };

  const FormSchema = Yup.object().shape({
    caseNumber: Yup.string().required('Case Number is required'),
    courtName: Yup.string().required('Jurisdiction is required'),
    primaryParty: Yup.string().required('Primary Party is required'),
    street: Yup.string().required('Address is required'),
    city: Yup.string().required('City is required'),
  });

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setServerError(null);
      const payload = {
        type: config.label,
        title: values.title || `${values.primaryParty} vs ${values.opposingParty}`,
        documentCode: values.documentCode,
        classification: values.classification,
        caseNumber: values.caseNumber,
        status: 'Draft',
        metadata: {
           court: values.courtName,
           fileRef: values.fileRef,
           parties: { applicant: { name: values.primaryParty, id: values.primaryId }, respondent: { name: values.opposingParty, id: values.opposingId } },
           serviceAddress: { street: values.street, city: values.city, province: values.province, code: values.postalCode },
           details: {
             marriageType: config.isDivorce ? values.marriageType : undefined,
             children: config.isDivorce ? values.childrenCount : undefined,
             claim: values.claimAmount,
             cause: values.causeOfAction,
             urgency: values.urgencyReason
           },
           financials: { tariff: values.baseTariff, vat: (values.baseTariff * VAT_RATE).toFixed(2), total: (values.baseTariff * (1 + VAT_RATE)).toFixed(2) }
        }
      };
      await apiPost('/documents', payload);
      navigate('/documents');
    } catch (err) {
      setServerError(err.response?.data?.message || err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Page>
      <Card>
        <Title>Drafting: {config.label}</Title>
        <p style={{color:'#6b7280', marginBottom:'24px'}}>Complete the matter particulars.</p>
        <Formik initialValues={initialValues} enableReinitialize validationSchema={FormSchema} onSubmit={handleSubmit}>
          {({ values, touched, errors, isSubmitting, setFieldValue, setFieldTouched, handleChange }) => (
            <Form>
              <SubTitle>Document Identity</SubTitle>
              <Grid3>
                <Row><Label>Document Code</Label><Input name="documentCode" disabled /></Row>
                <Row><Label>Your Ref</Label><Input name="fileRef" /></Row>
                <Row><Label>Case Number *</Label><Input name="caseNumber" placeholder="e.g. 12345/2025" /><ErrorText name="caseNumber" component="div" /></Row>
              </Grid3>

              <SubTitle>Jurisdiction</SubTitle>
              <Row>
                <Label>Selected Court *</Label>
                <div style={{position:'relative'}}>
                    <Input name="courtName" value={values.courtName} placeholder="Search High Courts & Magistrates..." onChange={(e) => { handleChange(e); setCourtSearch(e.target.value); setShowCourts(true); }} autoComplete="off" />
                    {showCourts && courtSearch.length > 0 && (
                        <SearchList>
                        {filteredCourts.slice(0, 6).map(c => (
                            <li key={c.id} onClick={() => { setFieldValue('courtName', c.name); setShowCourts(false); }}>
                            <div style={{fontWeight:600}}>{c.name}</div><div style={{fontSize:'0.75rem', color:'#6b7280'}}>{c.province} • {c.type}</div></li>
                        ))}
                        </SearchList>
                    )}
                </div>
                <ErrorText name="courtName" component="div" />
              </Row>

              <SubTitle>Parties</SubTitle>
              <Grid2>
                <Row><Label>{context.partyALabel} *</Label><Input name="primaryParty" placeholder="Name / Entity" /><ErrorText name="primaryParty" component="div" /></Row>
                <Row><Label>{context.idLabel}</Label><Input name="primaryId" placeholder={context.idPlaceholder} /></Row>
              </Grid2>
              <Grid2>
                <Row><Label>{context.partyBLabel}</Label><Input name="opposingParty" placeholder="Name / Entity" /></Row>
                <Row><Label>{context.idLabel}</Label><Input name="opposingId" placeholder={context.idPlaceholder} /></Row>
              </Grid2>

              <SubTitle>Service Address</SubTitle>
              <Row>
                <Label>Street Address *</Label>
                <AddressAutocomplete name="street" value={values.street} onChange={handleChange} error={touched.street && errors.street} placeholder="Start typing address..." onSelect={(place) => { setFieldValue('street', place.street); setFieldValue('city', place.city); setFieldValue('province', place.province); setFieldValue('postalCode', place.code); setFieldTouched('street', true, false); setFieldTouched('city', true, false); }} />
                <ErrorText name="street" component="div" />
              </Row>
              <Grid3>
                <Row><Label>City *</Label><Input name="city" /><ErrorText name="city" component="div" /></Row>
                <Row><Label>Province *</Label><Input name="province" /></Row>
                <Row><Label>Code</Label><Input name="postalCode" /></Row>
              </Grid3>

              {/* DYNAMIC SECTIONS */}
              {config.isDivorce && (
                  <>
                    <SubTitle>Marriage Particulars</SubTitle>
                    <Grid2>
                        <Row><Label>Marriage Regime</Label><Select as="select" name="marriageType"><option value="ANC_WITH">Out of Community (With Accrual)</option><option value="ANC_WITHOUT">Out of Community (No Accrual)</option><option value="COP">In Community of Property</option><option value="CUSTOMARY">Customary Marriage</option></Select></Row>
                        <Row><Label>Minor Children</Label><Input name="childrenCount" type="number" /></Row>
                    </Grid2>
                  </>
              )}

              {/* LITIGATION SPECIFICS */}
              {config.classification === 'LITIGATION' && (
                  <>
                     <SubTitle>Matter Details</SubTitle>
                     {(config.subType === 'combined_summons' || config.subType === 'simple_summons' || config.subType === 'debt_collection') && (
                        <Row><Label>Claim Amount (ZAR)</Label><Input name="claimAmount" type="number" /></Row>
                     )}
                     {config.subType === 'urgent_app' && (
                        <Row><Label>Grounds of Urgency</Label><TextArea as="textarea" name="urgencyReason" placeholder="Why is this matter urgent?" /></Row>
                     )}
                     <Row><Label>Cause of Action / Notes</Label><TextArea as="textarea" name="causeOfAction" placeholder="Brief summary of the matter..." /></Row>
                  </>
              )}

              {serverError && <div style={{color:'red', marginTop:10}}>{serverError}</div>}
              <ButtonPrimary type="submit" disabled={isSubmitting}>{isSubmitting ? 'Saving...' : 'Create Case File'}</ButtonPrimary>
            </Form>
          )}
        </Formik>
      </Card>

      <Card>
        <Title>Pro Forma Invoice</Title>
        <div style={{background:'#e0e7ff', color:'#4338ca', padding:'6px 10px', borderRadius:'6px', display:'inline-block', fontWeight:'600', fontSize:'0.75rem', marginBottom:'24px'}}>{config.label.toUpperCase()}</div>
        <div style={{ display: 'grid', gap: 12 }}>
          <Stat><span>Base Tariff</span><strong>R {config.baseFee?.toFixed(2)}</strong></Stat>
          <Stat><span>VAT (15%)</span><strong>R {(config.baseFee * 0.15).toFixed(2)}</strong></Stat>
          <Stat><span>TOTAL EST.</span><strong>R {(config.baseFee * 1.15).toFixed(2)}</strong></Stat>
        </div>
      </Card>
    </Page>
  );
};

export default UniversalLegalForm;
