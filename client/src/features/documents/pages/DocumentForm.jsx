// ~/client/src/features/documents/pages/DocumentForm.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage, useFormikContext } from 'formik';
import * as Yup from 'yup';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { apiPost, apiGet, apiPut } from '../../../services/apiService';
import { usePlacesWidget } from "react-google-autocomplete";

// ==========================================
// 🇿🇦 TARIFF ENGINE
// ==========================================
const TARIFFS = {
    'Summons': { base: 137.00, desc: 'Service of Summons' },
    'Combined Summons': { base: 137.00, desc: 'Service of Process' },
    'Notice of Motion': { base: 137.00, desc: 'Service of Notice' },
    'Warrant of Execution': { base: 195.00, desc: 'Execution against Property' },
    'Warrant of Ejectment': { base: 250.00, desc: 'Ejectment Order' },
    'Section 65 Proceedings': { base: 137.00, desc: 'Financial Enquiry' },
    'Garnishee Order': { base: 137.00, desc: 'Emoluments Attachment' },
    'Subpoena': { base: 137.00, desc: 'Service of Subpoena' },
    'Divorce Summons': { base: 137.00, desc: 'Personal Service Required' },
    'Interdict': { base: 137.00, desc: 'Urgent Application' },
    'Directive': { base: 137.00, desc: 'Court Directive' },
    'Letter of Demand': { base: 0.00, desc: 'Pre-litigation' },

    'Urgency_Surcharge': 300.00, 'Zone_1_Estimate': 65.00, 'VAT_Rate': 0.15
};

// ==========================================
// 🎨 STYLES
// ==========================================
const Layout = styled.div`
  display: grid; grid-template-columns: 2fr 1.2fr; gap: 2rem; max-width: 1200px; margin: 2rem auto; font-family: 'Segoe UI', system-ui, sans-serif;
  @media(max-width: 900px) { grid-template-columns: 1fr; }
`;
const FormCard = styled.div` background: white; padding: 2.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); border: 1px solid #e2e8f0; `;
const PricingCard = styled.div` background: #f8fafc; padding: 2rem; border-radius: 12px; border: 1px solid #e2e8f0; position: sticky; top: 2rem; `;
const Row = styled.div` display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.25rem; `;
const Label = styled.label` display: block; font-size: 0.85rem; font-weight: 600; color: #4a5568; margin-bottom: 6px; text-transform: uppercase; `;

const InputStyles = `
  width: 100%; padding: 12px; border: 1px solid #cbd5e0; border-radius: 8px; font-size: 0.95rem; box-sizing: border-box;
  &:focus { border-color: #3182ce; outline: none; box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1); }
`;
const StyledInput = styled.input`${InputStyles}`;
const StyledSelect = styled.select`${InputStyles} background: white; cursor: pointer;`;
const StyledTextarea = styled.textarea`${InputStyles}`;
const Button = styled.button` background: #3182ce; color: white; width: 100%; padding: 14px; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; margin-top: 1rem; &:disabled { background: #cbd5e0; } `;

// ==========================================
// 🧮 LIVE QUOTATION ENGINE
// ==========================================
const CostEstimator = () => {
    const { values, setFieldValue } = useFormikContext();
    const docType = TARIFFS[values.type] ? values.type : 'Summons';
    const baseData = TARIFFS[docType] || TARIFFS['Summons'];
    const baseFee = baseData.base;
    const urgencyFee = values.urgency === 'Urgent' ? TARIFFS.Urgency_Surcharge : 0;
    const travelFee = TARIFFS.Zone_1_Estimate;
    const subTotal = baseFee + urgencyFee + travelFee;
    const vat = subTotal * TARIFFS.VAT_Rate;
    const total = subTotal + vat;

    useEffect(() => {
        if (Math.abs(values.estimatedFee - total) > 0.01) {
            setFieldValue('estimatedFee', parseFloat(total.toFixed(2)));
        }
    }, [total, setFieldValue, values.estimatedFee]);

    return (
        <PricingCard>
            <h3 style={{ margin: '0 0 20px 0' }}>💰 Pro Forma Invoice</h3>
            <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between' }}><span>Service Fee</span><strong>R {baseFee.toFixed(2)}</strong></div>
            <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between' }}><span>Travel (Est.)</span><strong>R {travelFee.toFixed(2)}</strong></div>
            {values.urgency === 'Urgent' && <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between', color: '#e53e3e' }}><span>Urgency</span><strong>R {urgencyFee.toFixed(2)}</strong></div>}
            <hr style={{ borderColor: '#e2e8f0', margin: '15px 0' }} />
            <div style={{ fontSize: '1.4rem', fontWeight: '800', display: 'flex', justifyContent: 'space-between' }}><span>TOTAL</span><span>R {total.toFixed(2)}</span></div>
        </PricingCard>
    );
};

// ==========================================
// 📝 INSTRUCTION FORM
// ==========================================
const DocumentForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = !!id;

    const [initialValues, setInitialValues] = useState({
        caseNumber: '',
        type: 'Summons',
        urgency: 'Normal',
        plaintiff: '',
        defendant: '',
        address: '',
        notes: '',
        estimatedFee: 0
    });
    const [loading, setLoading] = useState(isEditMode);

    useEffect(() => {
        if (isEditMode) {
            const loadDoc = async () => {
                try {
                    console.log("🔄 Fetching document for edit:", id);
                    const res = await apiGet(`/documents/${id}`);

                    // ✅ ROBUST UNWRAPPING: Handles {data: ...} or direct object
                    let data = res.data || res;
                    if (data.data) data = data.data; // Unwrap if nested
                    if (data.document) data = data.document; // Unwrap if named 'document'

                    console.log("✅ Data Received for Form:", data);

                    setInitialValues({
                        caseNumber: data.caseNumber || '',
                        type: data.type || 'Summons',
                        urgency: data.urgency || 'Normal',
                        plaintiff: data.plaintiff || '',
                        defendant: data.defendant || '',
                        address: data.address || '',
                        notes: data.notes || '',
                        estimatedFee: data.estimatedFee || 0
                    });
                } catch (e) {
                    console.error("Load Error:", e);
                    toast.error("Error loading document");
                } finally {
                    setLoading(false);
                }
            };
            loadDoc();
        }
    }, [id, isEditMode]);

    const { ref: placeRef } = usePlacesWidget({
        apiKey: process.env.REACT_APP_GOOGLE_MAPS_KEY || "",
        options: { types: ["address"], componentRestrictions: { country: "za" } },
    });

    const handleSubmit = async (values, { setSubmitting }) => {
        try {
            if (isEditMode) {
                await apiPut(`/documents/${id}`, values);
                toast.success('Updated Successfully');
            } else {
                await apiPost('/documents', values);
                toast.success('Registered Successfully');
            }
            navigate('/dashboard');
        } catch (error) {
            toast.error('Failed to save');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div style={{ padding: '50px', textAlign: 'center' }}>Loading Editor...</div>;

    return (
        <Layout>
            <Formik
                // ✅ KEY PROP: This forces React to destroy and recreate the form when data loads
                key={isEditMode ? (initialValues.caseNumber || 'loading') : 'new'}
                enableReinitialize={true}
                initialValues={initialValues}
                validationSchema={Yup.object({
                    caseNumber: Yup.string().required('Required'),
                    plaintiff: Yup.string().required('Required'),
                    defendant: Yup.string().required('Required'),
                    address: Yup.string().required('Required'),
                })}
                onSubmit={handleSubmit}
            >
                {({ isSubmitting, setFieldValue, values }) => (
                    <>
                        <FormCard>
                            <h3 style={{ marginBottom: '20px' }}>📋 {isEditMode ? 'Edit Case' : 'New Instruction'}</h3>
                            <Form>
                                <Row>
                                    <div>
                                        <Label>Case Number</Label>
                                        {/* Direct Field Binding - No styling wrapper issues */}
                                        <Field name="caseNumber">
                                            {({ field }) => <StyledInput {...field} placeholder="e.g. 12345/2025" />}
                                        </Field>
                                        <ErrorMessage name="caseNumber" component="div" style={{ color: 'red', fontSize: '0.8rem' }} />
                                    </div>
                                    <div>
                                        <Label>Document Type</Label>
                                        <Field name="type">
                                            {({ field }) => (
                                                <StyledSelect {...field}>
                                                    {Object.keys(TARIFFS).filter(k => !['Urgency_Surcharge', 'Zone_1_Estimate', 'VAT_Rate'].includes(k)).map(key => (
                                                        <option key={key} value={key}>{key}</option>
                                                    ))}
                                                </StyledSelect>
                                            )}
                                        </Field>
                                    </div>
                                </Row>

                                <Row>
                                    <div><Label>Plaintiff</Label><Field name="plaintiff">{({ field }) => <StyledInput {...field} />}</Field></div>
                                    <div><Label>Defendant</Label><Field name="defendant">{({ field }) => <StyledInput {...field} />}</Field></div>
                                </Row>

                                <div style={{ marginBottom: '1.25rem' }}>
                                    <Label>Service Address</Label>
                                    <StyledInput
                                        ref={placeRef}
                                        value={values.address}
                                        onChange={(e) => setFieldValue('address', e.target.value)}
                                        placeholder="Enter physical address..."
                                    />
                                    <ErrorMessage name="address" component="div" style={{ color: 'red', fontSize: '0.8rem' }} />
                                </div>

                                <Row>
                                    <div>
                                        <Label>Urgency Level</Label>
                                        <div style={{ display: 'flex', gap: '15px', marginTop: '10px' }}>
                                            <label><Field type="radio" name="urgency" value="Normal" /> Normal</label>
                                            <label style={{ color: '#e53e3e', fontWeight: 'bold' }}><Field type="radio" name="urgency" value="Urgent" /> URGENT</label>
                                        </div>
                                    </div>
                                </Row>

                                <div style={{ marginBottom: '1.25rem' }}>
                                    <Label>Instruction Notes</Label>
                                    <Field name="notes">
                                        {({ field }) => <StyledTextarea {...field} rows="3" />}
                                    </Field>
                                </div>

                                <Button type="submit" disabled={isSubmitting}>
                                    {isSubmitting ? 'Saving...' : 'Save Instruction'}
                                </Button>
                            </Form>
                        </FormCard>
                        <CostEstimator />
                    </>
                )}
            </Formik>
        </Layout>
    );
};

export default DocumentForm;