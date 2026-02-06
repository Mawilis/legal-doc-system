/**
 * File: client/src/features/documents/components/DocumentForm.jsx
 * STATUS: EPITOME | LOCATION AWARE | PRODUCTION-READY
 * VERSION: 1.1.0
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - Context-aware document form with smart jurisdiction selector.
 * - Adds "Find Nearest" using browser Geolocation and the immutable SA_COURTS registry.
 *
 * COLLABORATION
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @product, @legal, @frontend, @security, @accessibility
 * -----------------------------------------------------------------------------
 */

import React, { useMemo, useState, useCallback, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { User, Building, Scale, FileText, Calendar, MapPin, Navigation } from 'lucide-react';
import { getFormType } from '../../../config/documentTypes';
import { SA_COURTS, getNearestCourt } from '../../../data/saCourts';
import { toast } from 'react-toastify';

/* Styled primitives (same as before) */
const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 1.5rem;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
`;

const FieldWrapper = styled.div`
  display: flex; flex-direction: column; gap: 0.5rem;
`;

const Label = styled.label`
  font-size: 0.85rem; font-weight: 700; color: #334155; display: flex; align-items: center; gap: 8px;
`;

const Input = styled.input`
  padding: 0.75rem; border: 1px solid #CBD5E1; border-radius: 8px; font-size: 0.95rem;
  transition: all 0.2s;
  &:focus { border-color: #2563EB; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); outline: none; }
`;

const Select = styled.select`
  padding: 0.75rem; border: 1px solid #CBD5E1; border-radius: 8px; font-size: 0.95rem;
  background-color: white;
  transition: all 0.2s;
  &:focus { border-color: #2563EB; outline: none; }
`;

const ButtonLink = styled.button`
  background: none;
  border: none;
  color: #2563EB;
  font-size: 0.75rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
`;

/* Component */
export default function DocumentForm({ category, formData, onChange, disabled = false }) {
    const formType = getFormType(category);

    const handleChange = useCallback((field, value) => {
        onChange({ ...formData, [field]: value });
    }, [formData, onChange]);

    // Find nearest using browser geolocation
    const handleAutoLocate = useCallback(() => {
        if (!navigator.geolocation) {
            return toast.error('Geolocation is not supported by your browser.');
        }

        const toastId = toast.loading('Triangulating nearest court...');

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                const nearest = getNearestCourt({ lat: latitude, lon: longitude });

                if (nearest) {
                    onChange({
                        ...formData,
                        courtId: nearest.id,
                        courtName: nearest.name
                    });
                    toast.update(toastId, { render: `Located: ${nearest.name}`, type: 'success', isLoading: false, autoClose: 3000 });
                } else {
                    toast.update(toastId, { render: 'No courts found with coordinates in registry.', type: 'warning', isLoading: false, autoClose: 3000 });
                }
            },
            (error) => {
                // eslint-disable-next-line no-console
                console.error('Geolocation error', error);
                toast.update(toastId, { render: 'Location access denied or unavailable.', type: 'error', isLoading: false, autoClose: 3000 });
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }, [formData, onChange]);

    return (
        <div>
            {formType === 'LITIGATION' && (
                <>
                    <h4 style={{ color: '#64748B', marginTop: 0, borderBottom: '1px solid #E2E8F0', paddingBottom: '8px' }}>
                        Court Details
                    </h4>

                    <FormGrid>
                        <FieldWrapper>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Label><Scale size={16} /> Jurisdiction / Court</Label>
                                <ButtonLink type="button" onClick={handleAutoLocate} disabled={disabled} aria-disabled={disabled}>
                                    <Navigation size={12} /> Find Nearest
                                </ButtonLink>
                            </div>

                            <Select
                                value={formData.courtId || ''}
                                onChange={e => {
                                    const court = SA_COURTS.find(c => c.id === e.target.value);
                                    onChange({
                                        ...formData,
                                        courtId: e.target.value,
                                        courtName: court ? court.name : ''
                                    });
                                }}
                                disabled={disabled}
                            >
                                <option value="">-- Select Competent Court --</option>
                                <optgroup label="Apex Courts">
                                    {SA_COURTS.filter(c => c.type === 'Apex').map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </optgroup>
                                <optgroup label="High Courts">
                                    {SA_COURTS.filter(c => c.type === 'High Court').map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </optgroup>
                                <optgroup label="Magistrates Courts">
                                    {SA_COURTS.filter(c => c.type === 'Magistrate').map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </optgroup>
                                <optgroup label="Labour Courts">
                                    {SA_COURTS.filter(c => c.type === 'Labour').map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </optgroup>
                            </Select>
                        </FieldWrapper>

                        <FieldWrapper>
                            <Label><FileText size={16} /> Case Number</Label>
                            <Input
                                placeholder="e.g. 12345/2024"
                                value={formData.caseNumber || ''}
                                onChange={e => handleChange('caseNumber', e.target.value)}
                                disabled={disabled}
                            />
                        </FieldWrapper>
                    </FormGrid>

                    <h4 style={{ color: '#64748B', marginTop: '2rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '8px' }}>
                        Parties
                    </h4>

                    <FormGrid>
                        <FieldWrapper>
                            <Label><User size={16} /> Plaintiff / Applicant</Label>
                            <Input
                                placeholder="Full Legal Name"
                                value={formData.plaintiff || ''}
                                onChange={e => handleChange('plaintiff', e.target.value)}
                                disabled={disabled}
                            />
                        </FieldWrapper>

                        <FieldWrapper>
                            <Label><User size={16} /> Defendant / Respondent</Label>
                            <Input
                                placeholder="Full Legal Name"
                                value={formData.defendant || ''}
                                onChange={e => handleChange('defendant', e.target.value)}
                                disabled={disabled}
                            />
                        </FieldWrapper>
                    </FormGrid>
                </>
            )}

            {formType === 'AGREEMENT' && (
                <>
                    <h4 style={{ color: '#64748B', marginTop: 0, borderBottom: '1px solid #E2E8F0', paddingBottom: '8px' }}>
                        Contracting Parties
                    </h4>

                    <FormGrid>
                        <FieldWrapper>
                            <Label><Building size={16} /> Party A (Provider/Landlord)</Label>
                            <Input
                                placeholder="Name or Company"
                                value={formData.partyA || ''}
                                onChange={e => handleChange('partyA', e.target.value)}
                                disabled={disabled}
                            />
                        </FieldWrapper>

                        <FieldWrapper>
                            <Label><User size={16} /> Party B (Client/Tenant)</Label>
                            <Input
                                placeholder="Name or Company"
                                value={formData.partyB || ''}
                                onChange={e => handleChange('partyB', e.target.value)}
                                disabled={disabled}
                            />
                        </FieldWrapper>
                    </FormGrid>

                    <FormGrid>
                        <FieldWrapper>
                            <Label><Calendar size={16} /> Effective Date</Label>
                            <Input
                                type="date"
                                value={formData.effectiveDate || ''}
                                onChange={e => handleChange('effectiveDate', e.target.value)}
                                disabled={disabled}
                            />
                        </FieldWrapper>

                        <FieldWrapper>
                            <Label><MapPin size={16} /> Jurisdiction/Place</Label>
                            <Input
                                placeholder="e.g. Sandton, Johannesburg"
                                value={formData.jurisdiction || ''}
                                onChange={e => handleChange('jurisdiction', e.target.value)}
                                disabled={disabled}
                            />
                        </FieldWrapper>
                    </FormGrid>
                </>
            )}
        </div>
    );
}

DocumentForm.propTypes = {
    category: PropTypes.string.isRequired,
    formData: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired,
    disabled: PropTypes.bool
};

DocumentForm.defaultProps = {
    disabled: false
};
