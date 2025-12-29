/**
 * Divorce Settlement – Billion-Dollar Master Form
 * ------------------------------------------------
 */
import React, { useMemo, useState } from 'react';
import styled from 'styled-components';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useNavigate } from 'react-router-dom';
import { apiPost } from '../../../services/http'; 

// --- Styled Components ---
const Page = styled.div`
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
  padding: 40px;
  background: #f7f9fc;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  min-height: 100vh;
`;
const Card = styled.div`
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  padding: 30px;
  border: 1px solid rgba(0,0,0,0.02);
`;
const Title = styled.h1`
  font-size: 1.6rem;
  margin: 0 0 8px 0;
  color: #1b1f23;
  font-weight: 700;
`;
const SubTitle = styled.h2`
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 24px 0 16px 0;
  color: #8898aa;
  font-weight: 700;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
`;
const Grid2 = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
`;
const Grid3 = styled.div`
  display: grid;
  grid-template-columns: 1.4fr 0.8fr 0.8fr;
  gap: 20px;
`;
const Label = styled.label`
  display: block;
  font-size: 0.9rem;
  color: #374151;
  margin-bottom: 8px;
  font-weight: 600;
`;
const Input = styled(Field)`
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
  background: #f9fafb;
  &:focus {
    outline: none;
    background: #fff;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }
`;
const Select = styled(Field)`
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  background: #f9fafb;
`;
const ErrorText = styled(ErrorMessage)`
  color: #dc2626;
  font-size: 0.8rem;
  margin-top: 6px;
`;
const ButtonPrimary = styled.button`
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  color: #fff;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 20px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  &:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(30,64,175,0.25); }
  &:disabled { background: #9ca3af; cursor: not-allowed; }
`;
const Stat = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px dashed #e5e7eb;
  font-size: 0.95rem;
  &:last-child { border-bottom: none; font-weight: 700; font-size: 1.1rem; color: #1e40af; }
`;
const Badge = styled.span`
  display: inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  background: #eef2ff;
  color: #3730a3;
  text-transform: uppercase;
`;
const Help = styled.p`
  font-size: 0.85rem;
  color: #6b7280;
  margin: 6px 0 12px 0;
  line-height: 1.5;
`;
const Divider = styled.hr`
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 24px 0;
`;
const Row = styled.div`
  margin-bottom: 16px;
`;

// --- Constants ---
const DOC_TYPE = 'Divorce Settlement Agreement';
const CLASSIFICATIONS = ['FAMILY', 'LITIGATION', 'PRE-LITIGATION', 'PROPERTY', 'COMMERCIAL'];
const URGENCY = ['normal', 'urgent'];
const BASE_TARIFF_DEFAULT = 2500;
const VAT_RATE = 0.15;

// --- Validation Schema ---
const FormSchema = Yup.object().shape({
  classification: Yup.string().required('Classification is required'),
  caseNumber: Yup.string().required('Case number is required'),
  fileRef: Yup.string().required('Your file reference is required'),
  courtName: Yup.string().required('Court is required'),
  primaryParty: Yup.string().required('Primary party is required'),
  primaryId: Yup.string().required('Primary ID/Reg No is required'),
  opposingParty: Yup.string().required('Opposing party is required'),
  opposingId: Yup.string().required('Opposing ID/Reg No is required'),
  street: Yup.string().required('Street is required'),
  city: Yup.string().required('City is required'),
  province: Yup.string().required('Province is required'),
  postalCode: Yup.string().required('Postal code is required'),
  baseTariff: Yup.number().min(0).required('Base tariff is required'),
  title: Yup.string().required('Title is required'),
  documentCode: Yup.string().required('Document code is required'),
});

// --- Helper: build clean payload for backend ---
function buildPayload(values) {
  const {
    classification, caseNumber, fileRef, courtName, primaryParty, primaryId, opposingParty, opposingId,
    street, city, province, postalCode, urgency, baseTariff, title, documentCode
  } = values;

  const vat = Math.round(baseTariff * VAT_RATE * 100) / 100;
  const total = Math.round((baseTariff + vat) * 100) / 100;

  return {
    type: DOC_TYPE,
    title,
    documentCode,
    classification,
    caseNumber, 
    status: 'Draft',
    metadata: {
       fileRef,
       court: courtName,
       parties: {
         plaintiff: { name: primaryParty, id: primaryId, role: 'Applicant/Plaintiff' },
         defendant: { name: opposingParty, id: opposingId, role: 'Respondent/Defendant' }
       },
       serviceAddress: { street, city, province, postalCode },
       urgency,
       financials: { tariff: baseTariff, vat, total }
    }
  };
}

// --- Component ---
const DivorceSettlementForm = () => {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState(null);

  const initialValues = useMemo(() => ({
    classification: 'FAMILY',
    caseNumber: '',
    fileRef: '',
    courtName: '',
    primaryParty: '',
    primaryId: '',
    opposingParty: '',
    opposingId: '',
    street: '',
    city: '',
    province: '',
    postalCode: '',
    urgency: 'normal',
    baseTariff: BASE_TARIFF_DEFAULT,
    title: '',
    documentCode: '',
  }), []);

  const calcVat = (base) => Math.round(base * VAT_RATE * 100) / 100;
  const calcTotal = (base) => Math.round((base + calcVat(base)) * 100) / 100;

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setServerError(null);
      const payload = buildPayload(values);
      // SECURE POST
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
        <Title>Drafting: Divorce Settlement</Title>
        <Help>Complete all required fields below. Invoice updates automatically. Secured by End-to-End Encryption.</Help>
        <Divider />

        <Formik
          initialValues={initialValues}
          validationSchema={FormSchema}
          onSubmit={handleSubmit}
        >
          {({ values, isSubmitting, setFieldValue }) => (
            <Form>
              <SubTitle>Document Identity</SubTitle>
              <Grid3>
                <Row><Label>Type</Label><Input name="type" value={DOC_TYPE} disabled /><Help>Fixed Type</Help></Row>
                <Row><Label>Title</Label><Input name="title" placeholder="e.g. Smith vs Smith" /><ErrorText name="title" component="div" /></Row>
                <Row><Label>Document Code</Label><Input name="documentCode" placeholder="e.g. DIV-001" /><ErrorText name="documentCode" component="div" /></Row>
              </Grid3>

              <SubTitle>Jurisdiction & Court</SubTitle>
              <Grid2>
                <Row><Label>Case Number</Label><Input name="caseNumber" placeholder="12345/2025" /><ErrorText name="caseNumber" component="div" /></Row>
                <Row><Label>Your Ref</Label><Input name="fileRef" placeholder="MAT101/WK" /><ErrorText name="fileRef" component="div" /></Row>
              </Grid2>
              <Row><Label>Selected Court</Label><Input name="courtName" placeholder="Search Courts..." /><ErrorText name="courtName" component="div" /></Row>

              <SubTitle>Parties (Litigants)</SubTitle>
              <Grid2>
                <Row><Label>Plaintiff</Label><Input name="primaryParty" /><ErrorText name="primaryParty" component="div" /></Row>
                <Row><Label>ID / Reg</Label><Input name="primaryId" /><ErrorText name="primaryId" component="div" /></Row>
              </Grid2>
              <Grid2>
                <Row><Label>Defendant</Label><Input name="opposingParty" /><ErrorText name="opposingParty" component="div" /></Row>
                <Row><Label>ID / Reg</Label><Input name="opposingId" /><ErrorText name="opposingId" component="div" /></Row>
              </Grid2>

              <SubTitle>Service Address</SubTitle>
              <Grid2>
                <Row><Label>Street</Label><Input name="street" /><ErrorText name="street" component="div" /></Row>
                <Row><Label>City</Label><Input name="city" /><ErrorText name="city" component="div" /></Row>
              </Grid2>
              <Grid2>
                <Row><Label>Province</Label><Input name="province" /><ErrorText name="province" component="div" /></Row>
                <Row><Label>Postal Code</Label><Input name="postalCode" /><ErrorText name="postalCode" component="div" /></Row>
              </Grid2>

              <SubTitle>Financials</SubTitle>
              <Grid3>
                <Row>
                  <Label>Base Tariff (R)</Label>
                  <Input name="baseTariff" type="number" onChange={(e) => setFieldValue('baseTariff', Number(e.target.value))} />
                  <ErrorText name="baseTariff" component="div" />
                </Row>
                <Row><Label>VAT (15%)</Label><Input name="vat" value={calcVat(values.baseTariff)} disabled /></Row>
                <Row><Label>Total</Label><Input name="total" value={calcTotal(values.baseTariff)} disabled /></Row>
              </Grid3>

              {serverError && (
                <div style={{ marginTop: 12, color: '#dc2626', background: '#fee2e2', padding: '10px', borderRadius: 8 }}>
                  ⚠️ {serverError}
                </div>
              )}

              <ButtonPrimary type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Processing...' : 'Generate & Save Instruction'}
              </ButtonPrimary>
            </Form>
          )}
        </Formik>
      </Card>

      {/* Invoice Panel */}
      <Card>
        <Title>Pro Forma Invoice</Title>
        <Badge>{DOC_TYPE}</Badge>
        <Divider />
        <SubTitle>Estimate</SubTitle>
        <div style={{ display: 'grid', gap: 8 }}>
          <Stat><span>Base Tariff</span><strong>R {BASE_TARIFF_DEFAULT.toFixed(2)}</strong></Stat>
          <Stat><span>VAT (15%)</span><strong>R {(BASE_TARIFF_DEFAULT * VAT_RATE).toFixed(2)}</strong></Stat>
          <Stat><span>TOTAL EST.</span><strong>R {(BASE_TARIFF_DEFAULT * (1 + VAT_RATE)).toFixed(2)}</strong></Stat>
        </div>
      </Card>
    </Page>
  );
};

export default DivorceSettlementForm;
