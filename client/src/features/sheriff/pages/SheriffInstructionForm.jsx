import React, { useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { apiPost } from '../../../services/http'; 
import AddressAutocomplete from '../../../components/AddressAutocomplete';

const Page = styled.div` padding: 40px; background: #f0f4f8; font-family: 'Inter', sans-serif; min-height: 100vh; display: grid; grid-template-columns: 1fr 380px; gap: 30px; `;
const Card = styled.div` background: #fff; border-radius: 12px; padding: 30px; margin-bottom: 24px; border: 1px solid #e1e4e8; `;
const SectionTitle = styled.h3` font-size: 0.95rem; font-weight: 700; margin: 0 0 20px 0; border-bottom: 1px solid #eee; padding-bottom: 10px; `;
const Grid2 = styled.div` display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 15px; `;
const Label = styled.label` display: block; font-size: 0.85rem; margin-bottom: 6px; font-weight: 600; `;
const Input = styled(Field)` width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; background:#fff; `;
const Select = styled(Field)` width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; background:#fff; `;
const ButtonPrimary = styled.button` width: 100%; padding: 16px; background: #0f172a; color: #fff; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; margin-top:10px; `;

const SERVICE_TYPES = [
  { id: 'summons', label: '1. Service of Summons', base: 180, plan: '3 Attempts / 7 Days' },
  { id: 'urgent', label: '2. Urgent Service (Rule 6(12))', base: 450, plan: 'Immediate / 24 Hours' },
  { id: 'writ_movable', label: '3. Writ of Execution (Movables)', base: 950, plan: 'Attachment & Inventory' },
  { id: 'eviction', label: '5. Ejectment / Eviction', base: 1500, plan: 'SAPS Coordination Required' }
];

const calculatePricing = (typeId, distance, urgency) => {
  const type = SERVICE_TYPES.find(t => t.id === typeId) || SERVICE_TYPES[0];
  let total = type.base + (distance * 6.50);
  if (urgency === 'urgent') total *= 1.5;
  return { base: type.base, total: total * 1.15 }; // Incl VAT
};

export default function SheriffInstructionForm() {
  const navigate = useNavigate();
  const initialValues = { title: '', caseNumber: '', court: '', plaintiff: '', serviceType: 'summons', street: '', city: '', province: '', postalCode: '', urgency: 'normal', distanceKm: 15, documentCode: `SHF-${Date.now()}` };

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      const typeDef = SERVICE_TYPES.find(t => t.id === values.serviceType);
      const financials = calculatePricing(values.serviceType, values.distanceKm, values.urgency);
      const payload = {
        ...values,
        attemptPlan: { window: typeDef.plan, minAttempts: 3 },
        pricing: financials,
        serviceAddress: `${values.street}, ${values.city}, ${values.province}`,
        classification: 'SHERIFF',
        status: 'Pending Dispatch'
      };
      await apiPost('/dispatch-instructions', payload);
      navigate('/documents');
    } catch (err) { alert(err.message); } finally { setSubmitting(false); }
  };

  return (
    <Page>
      <Formik initialValues={initialValues} onSubmit={handleSubmit}>
        {({ values, setFieldValue, handleChange, isSubmitting }) => {
          const financials = calculatePricing(values.serviceType, values.distanceKm, values.urgency);
          return (
            <Form>
              <Card>
                <SectionTitle>⚖️ Case Identity</SectionTitle>
                <Grid2><div><Label>Title</Label><Input name="title" /></div><div><Label>Code</Label><Input name="documentCode" disabled /></div></Grid2>
                <Grid2><div><Label>Case Number</Label><Input name="caseNumber" /></div><div><Label>Court</Label><Input name="court" /></div></Grid2>
                <Grid2><div><Label>Plaintiff</Label><Input name="plaintiff" /></div><div><Label>Service Type</Label><Select as="select" name="serviceType">{SERVICE_TYPES.map(t=><option key={t.id} value={t.id}>{t.label}</option>)}</Select></div></Grid2>
                <Label>Address</Label>
                <AddressAutocomplete name="street" value={values.street} onChange={handleChange} onSelect={p => { setFieldValue('street', p.street); setFieldValue('city', p.city); setFieldValue('province', p.province); }} />
              </Card>
              <ButtonPrimary type="submit" disabled={isSubmitting}>{isSubmitting ? 'DISPATCHING...' : 'GENERATE INSTRUCTION'}</ButtonPrimary>
              <Card style={{marginTop: 20}}>
                <SectionTitle>💰 Est. Cost</SectionTitle>
                <div>Base: R {financials.base} | Total (VAT Inc): R {financials.total.toFixed(2)}</div>
              </Card>
            </Form>
          );
        }}
      </Formik>
    </Page>
  );
}