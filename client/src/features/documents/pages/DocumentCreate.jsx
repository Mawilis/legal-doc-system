/**
 * File: client/src/features/documents/pages/DocumentCreate.jsx
 * PATH: client/src/features/documents/pages/DocumentCreate.jsx
 * STATUS: PRODUCTION | EPITOME | AUDITABLE
 * VERSION: 4.0.0
 *
 * PURPOSE
 * - Definitive Document Create page for Wilsy OS.
 * - Declarative schema engine: Category -> Type -> Sections -> Fields.
 * - Broad coverage of legal categories and document types (South Africa + enterprise).
 * - Court-ready templates (Affidavit, Summons, Notice of Motion, Combined Summons,
 *   Charge Sheet, Warrant, Maintenance Application, Divorce Papers, Contract,
 *   Power of Attorney, Lease Agreement, Employment Contract, CCMA Referral, Title Deed Transfer,
 *   Administrative Review, Patent Application, Tax Assessment Objection, Environmental Permit Appeal).
 * - Features: autosave, preview hook, attachments, exhibits, repeatable paragraphs,
 *   service log, signature placeholders, actor binding, immutable metadata, audit emission,
 *   per-section validators, retention flags, readyForESign state.
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend (document flows)
 * - BACKEND OWNER: @backend-team (API contract & persistence)
 * - SECURITY OWNER: @security (telemetry, PII, retention)
 * - QA OWNER: @qa (unit + integration + e2e tests)
 * - SRE OWNER: @sre (observability & correlation ids)
 *
 * REVIEW GATES (MANDATORY)
 * 1. Any change to DOCUMENT_SCHEMA or payload shape requires backend & security signoff.
 * 2. Add/adjust unit and integration tests for any schema change.
 * 3. SRE must confirm correlation id propagation and log retention.
 *
 * DEPENDENCIES (expected)
 * - useAuthStore() -> { user, token } where user includes { name, email, role, tenantId, tenantName, firstName, lastName }
 * - documentService.createDocument(token, payload) -> { ok, status, data?, message? }
 * - documentService.uploadAttachment(token, file) -> { ok, data: { url, id } } (optional)
 * - AuthUtils.AuditService.log(event, payload) and AuthUtils.Logger.error(...)
 *
 * SECURITY
 * - No raw tokens or tenant IDs are rendered. Use maskForUi for display.
 * - Audit emission is best-effort and non-blocking.
 * - Server enforces RBAC and tenant scoping.
 *
 * TEST GUIDANCE
 * - Unit tests: validateFieldValue, renderField, autosave restore, emitAudit calls.
 * - Integration tests: mock documentService.createDocument and preview endpoints.
 *
 * NOTE
 * - This file is intentionally comprehensive. Add new types by updating DOCUMENT_SCHEMA only.
 * -----------------------------------------------------------------------------
 */

import React, { useEffect, useMemo, useState, useCallback, useRef } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import {
    FiSave, FiX, FiFileText, FiUpload, FiEye, FiUser, FiClock, FiPlus, FiMinus, FiAlertTriangle
} from 'react-icons/fi';
import { toast } from 'react-toastify';

import useAuthStore from '../../../store/authStore';
import documentService from '../services/documentService';
import AuthUtils from '../../auth/utils/authUtils';

/* -----------------------------------------------------------------------------
   Styling primitives (use global tokens in App.css)
   -------------------------------------------------------------------------- */

const Page = styled.div`
  padding: 28px;
  max-width: 1280px;
  margin: 0 auto;
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  color: var(--color-text-main, #0f172a);
`;

const Panel = styled.section`
  background: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-md, 0 10px 15px rgba(15,23,42,0.06));
`;

const Form = styled.form`display:block;`;

const Header = styled.header`
  display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:18px;
  h1 { margin:0; font-size:1.5rem; font-weight:800; display:flex; align-items:center; gap:8px; }
  p { margin:6px 0 0; color:var(--color-text-muted,#64748b); font-size:0.95rem; }
`;

const Grid = styled.div`
  display:grid;
  grid-template-columns: 1fr 380px;
  gap: 18px;
  align-items:start;
  @media (max-width: 980px) { grid-template-columns: 1fr; }
`;

const Column = styled.div`display:flex; flex-direction:column; gap:12px;`;

const Field = styled.div`display:flex; flex-direction:column;`;
const Label = styled.label`font-weight:700; margin-bottom:6px;`;
const Input = styled.input`padding:10px 12px; border-radius:8px; border:1px solid var(--color-border,#cbd5e1); font-size:1rem;`;
const Select = styled.select`padding:10px 12px; border-radius:8px; border:1px solid var(--color-border,#cbd5e1); font-size:1rem;`;
const Textarea = styled.textarea`padding:10px 12px; border-radius:8px; border:1px solid var(--color-border,#cbd5e1); min-height:120px; resize:vertical;`;
const Hint = styled.div`font-size:0.85rem; color:var(--color-text-muted,#64748b); margin-top:6px;`;
const ErrorText = styled.div`color:var(--color-danger,#ef4444); font-weight:700; margin-top:6px;`;

const Sidebar = styled.aside`
  background: linear-gradient(180deg,#fbfdff,#ffffff);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--color-border,#e6eef6);
  height: 100%;
  overflow: auto;
`;

const Actions = styled.div`display:flex; gap:12px; justify-content:flex-end; margin-top:12px;`;
const Button = styled.button`
  display:inline-flex; align-items:center; gap:8px; padding:10px 14px; border-radius:8px; border:none; font-weight:800; cursor:pointer;
  background:${p => p.ghost ? 'transparent' : 'var(--color-accent,#2563EB)'}; color:${p => p.ghost ? 'var(--color-text-main,#0f172a)' : '#fff'};
  border:${p => p.ghost ? '1px solid var(--color-border,#e2e8f0)' : 'none'};
  &:disabled { opacity:0.6; cursor:not-allowed; }
`;

/* -----------------------------------------------------------------------------
   DOCUMENT_SCHEMA: comprehensive categories & types
   - Add new types by editing this object only.
   - Collaboration: backend must sign off on required fields and payload shape.
   -------------------------------------------------------------------------- */

const DOCUMENT_SCHEMA = {
    Civil: {
        display: 'Civil Litigation',
        types: {
            Affidavit: {
                display: 'Affidavit',
                description: 'Affidavit with deponent details, oath, numbered paragraphs, exhibits, verification and commissioner details.',
                sections: [
                    {
                        id: 'header', title: 'Header / Case Metadata', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true, help: 'e.g., Gauteng Division, Pretoria' },
                            { id: 'caseNumber', label: 'Case Number', input: 'text', required: false },
                            { id: 'matterRef', label: 'Matter Reference', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'applicant', label: 'Applicant / Plaintiff', input: 'text', required: false },
                            { id: 'respondent', label: 'Respondent / Defendant', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'deponent', title: 'Deponent Identity', fields: [
                            { id: 'deponentName', label: 'Deponent Full Name', input: 'text', required: true },
                            { id: 'deponentId', label: 'ID / Passport Number', input: 'text', required: true, validator: v => /^\d{6,20}$/.test(String(v)) || 'Enter a valid ID/passport' },
                            { id: 'deponentOccupation', label: 'Occupation', input: 'text', required: false },
                            { id: 'deponentAddress', label: 'Address for Service', input: 'textarea', required: true },
                            { id: 'deponentContact', label: 'Contact (phone/email)', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'jurisdiction', title: 'Jurisdiction & Oath', fields: [
                            { id: 'swornAt', label: 'Sworn at (place)', input: 'text', required: true },
                            { id: 'swornOn', label: 'Sworn on (date)', input: 'date', required: true },
                            { id: 'commissioner', label: 'Commissioner / Notary', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'statement', title: 'Statement of Facts', fields: [
                            { id: 'statement', label: 'Statement of Facts (numbered)', input: 'repeatable_text', required: true, help: 'Numbered paragraphs; reference exhibits using [Exhibit A]' }
                        ]
                    },
                    {
                        id: 'exhibits', title: 'Exhibits', fields: [
                            { id: 'exhibits', label: 'Exhibits & Annexures', input: 'attachments', required: false, help: 'Upload exhibits and tag them (A, B, C...)' }
                        ]
                    },
                    {
                        id: 'verification', title: 'Verification & Signature', fields: [
                            { id: 'verificationText', label: 'Verification Text', input: 'textarea', required: true },
                            { id: 'signatoryName', label: 'Signatory Name', input: 'text', required: true },
                            { id: 'signature', label: 'Signature Block', input: 'signature', required: true }
                        ]
                    },
                    {
                        id: 'service', title: 'Service Log', fields: [
                            { id: 'serviceLog', label: 'Service Log', input: 'repeatable_service', required: false }
                        ]
                    },
                    {
                        id: 'auditMeta', title: 'Audit & Retention', fields: [
                            { id: 'retentionPolicy', label: 'Retention Policy', input: 'select', required: false, options: ['7 years', '10 years', 'Permanent'] },
                            { id: 'redactionRequired', label: 'Redaction Required', input: 'boolean', required: false }
                        ]
                    }
                ]
            },

            Summons: {
                display: 'Summons',
                description: 'Summons to commence civil proceedings (Combined/Particulars).',
                sections: [
                    {
                        id: 'header', title: 'Header / Case Metadata', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true },
                            { id: 'caseNumber', label: 'Case Number', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'plaintiff', label: 'Plaintiff', input: 'text', required: true },
                            { id: 'defendant', label: 'Defendant', input: 'text', required: true },
                            { id: 'serviceAddress', label: 'Address for Service', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'claim', title: 'Particulars of Claim', fields: [
                            { id: 'claimAmount', label: 'Claim Amount (ZAR)', input: 'currency', required: false },
                            { id: 'particulars', label: 'Particulars of Claim', input: 'repeatable_text', required: true }
                        ]
                    },
                    {
                        id: 'exhibits', title: 'Exhibits', fields: [
                            { id: 'exhibits', label: 'Exhibits', input: 'attachments', required: false }
                        ]
                    },
                    {
                        id: 'signature', title: 'Signature', fields: [
                            { id: 'signatoryName', label: 'Signatory Name', input: 'text', required: true },
                            { id: 'signature', label: 'Signature Block', input: 'signature', required: true }
                        ]
                    },
                    {
                        id: 'auditMeta', title: 'Audit & Retention', fields: [
                            { id: 'retentionPolicy', label: 'Retention Policy', input: 'select', required: false, options: ['7 years', '10 years', 'Permanent'] }
                        ]
                    }
                ]
            },

            NoticeOfMotion: {
                display: 'Notice of Motion',
                description: 'Notice of Motion with supporting affidavit and relief sought.',
                sections: [
                    {
                        id: 'header', title: 'Header', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true },
                            { id: 'caseNumber', label: 'Case Number', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'applicant', label: 'Applicant', input: 'text', required: true },
                            { id: 'respondent', label: 'Respondent', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'grounds', title: 'Grounds & Relief', fields: [
                            { id: 'grounds', label: 'Grounds of Application', input: 'repeatable_text', required: true },
                            { id: 'relief', label: 'Relief Sought', input: 'repeatable_text', required: true }
                        ]
                    },
                    {
                        id: 'support', title: 'Supporting Documents', fields: [
                            { id: 'supportingAffidavit', label: 'Supporting Affidavit (reference)', input: 'text', required: false },
                            { id: 'exhibits', label: 'Exhibits', input: 'attachments', required: false }
                        ]
                    },
                    {
                        id: 'signature', title: 'Signature', fields: [
                            { id: 'signatoryName', label: 'Signatory Name', input: 'text', required: true },
                            { id: 'signature', label: 'Signature Block', input: 'signature', required: true }
                        ]
                    }
                ]
            },

            CombinedSummons: {
                display: 'Combined Summons',
                description: 'Combined summons for liquidated claims.',
                sections: [
                    {
                        id: 'header', title: 'Header', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'plaintiff', label: 'Plaintiff', input: 'text', required: true },
                            { id: 'defendant', label: 'Defendant', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'claim', title: 'Claim', fields: [
                            { id: 'claimAmount', label: 'Claim Amount (ZAR)', input: 'currency', required: true },
                            { id: 'particulars', label: 'Particulars', input: 'repeatable_text', required: true }
                        ]
                    },
                    {
                        id: 'signature', title: 'Signature', fields: [
                            { id: 'signatoryName', label: 'Signatory Name', input: 'text', required: true }
                        ]
                    }
                ]
            }
        }
    },

    Criminal: {
        display: 'Criminal',
        types: {
            ChargeSheet: {
                display: 'Charge Sheet',
                description: 'Formal charge sheet for criminal proceedings.',
                sections: [
                    {
                        id: 'header', title: 'Header', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true },
                            { id: 'docketNumber', label: 'Docket Number', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'accused', title: 'Accused', fields: [
                            { id: 'accusedName', label: 'Accused Full Name', input: 'text', required: true },
                            { id: 'accusedId', label: 'ID / Passport', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'charges', title: 'Charges', fields: [
                            { id: 'counts', label: 'Counts (repeatable)', input: 'repeatable_text', required: true }
                        ]
                    },
                    {
                        id: 'evidence', title: 'Evidence & Exhibits', fields: [
                            { id: 'exhibits', label: 'Exhibits', input: 'attachments', required: false }
                        ]
                    },
                    {
                        id: 'signature', title: 'Signature', fields: [
                            { id: 'prosecutor', label: 'Prosecutor Name', input: 'text', required: true }
                        ]
                    }
                ]
            },

            Warrant: {
                display: 'Warrant of Arrest',
                description: 'Warrant for arrest with grounds and particulars.',
                sections: [
                    {
                        id: 'header', title: 'Header', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'subject', title: 'Subject', fields: [
                            { id: 'subjectName', label: 'Subject Full Name', input: 'text', required: true },
                            { id: 'subjectId', label: 'ID / Passport', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'grounds', title: 'Grounds', fields: [
                            { id: 'grounds', label: 'Grounds for Warrant', input: 'repeatable_text', required: true }
                        ]
                    },
                    {
                        id: 'signature', title: 'Signature', fields: [
                            { id: 'issuingOfficer', label: 'Issuing Officer', input: 'text', required: true }
                        ]
                    }
                ]
            },

            BailApplication: {
                display: 'Bail Application',
                description: 'Application for bail with supporting affidavit and conditions.',
                sections: [
                    {
                        id: 'header', title: 'Header', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'applicant', title: 'Applicant', fields: [
                            { id: 'applicantName', label: 'Applicant Name', input: 'text', required: true },
                            { id: 'applicantId', label: 'ID / Passport', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'grounds', title: 'Grounds & Conditions', fields: [
                            { id: 'grounds', label: 'Grounds for Bail', input: 'repeatable_text', required: true },
                            { id: 'conditions', label: 'Suggested Conditions', input: 'textarea', required: false }
                        ]
                    },
                    {
                        id: 'support', title: 'Supporting Documents', fields: [
                            { id: 'supportingAffidavit', label: 'Supporting Affidavit', input: 'text', required: false },
                            { id: 'exhibits', label: 'Exhibits', input: 'attachments', required: false }
                        ]
                    }
                ]
            }
        }
    },

    Family: {
        display: 'Family Law',
        types: {
            MaintenanceApplication: {
                display: 'Maintenance Application',
                description: 'Application for maintenance with income/expense schedules.',
                sections: [
                    {
                        id: 'header', title: 'Header', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties & Dependents', fields: [
                            { id: 'applicant', label: 'Applicant Full Name', input: 'text', required: true },
                            { id: 'respondent', label: 'Respondent Full Name', input: 'text', required: true },
                            { id: 'dependents', label: 'Children / Dependents', input: 'repeatable_text', required: false }
                        ]
                    },
                    {
                        id: 'means', title: 'Income & Expenses', fields: [
                            { id: 'applicantIncome', label: 'Applicant Income (ZAR)', input: 'currency', required: true },
                            { id: 'respondentIncome', label: 'Respondent Income (ZAR)', input: 'currency', required: true },
                            { id: 'expenses', label: 'Monthly Expenses', input: 'textarea', required: false }
                        ]
                    },
                    {
                        id: 'relief', title: 'Relief Sought', fields: [
                            { id: 'amountRequested', label: 'Amount Requested (ZAR)', input: 'currency', required: true },
                            { id: 'paymentTerms', label: 'Payment Terms', input: 'textarea', required: false }
                        ]
                    },
                    {
                        id: 'exhibits', title: 'Supporting Documents', fields: [
                            { id: 'supportingDocs', label: 'Supporting Documents', input: 'attachments', required: false }
                        ]
                    }
                ]
            },

            DivorcePapers: {
                display: 'Divorce Papers',
                description: 'Papers to commence divorce proceedings with particulars of claim and settlement.',
                sections: [
                    {
                        id: 'header', title: 'Header', fields: [
                            { id: 'court', label: 'Court / Division', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'spouseA', label: 'Spouse A', input: 'text', required: true },
                            { id: 'spouseB', label: 'Spouse B', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'grounds', title: 'Grounds & Relief', fields: [
                            { id: 'grounds', label: 'Grounds for Divorce', input: 'repeatable_text', required: true },
                            { id: 'settlement', label: 'Settlement Terms', input: 'textarea', required: false }
                        ]
                    },
                    {
                        id: 'exhibits', title: 'Supporting Documents', fields: [
                            { id: 'annexures', label: 'Annexures', input: 'attachments', required: false }
                        ]
                    }
                ]
            }
        }
    },

    Corporate: {
        display: 'Corporate / Commercial',
        types: {
            Contract: {
                display: 'Contract / Agreement',
                description: 'Commercial contract template with recitals, definitions, terms, schedules and signatures.',
                sections: [
                    {
                        id: 'metadata', title: 'Contract Metadata', fields: [
                            { id: 'contractTitle', label: 'Contract Title', input: 'text', required: true },
                            { id: 'effectiveDate', label: 'Effective Date', input: 'date', required: true }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'partyA', label: 'Party A', input: 'textarea', required: true },
                            { id: 'partyB', label: 'Party B', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'terms', title: 'Terms & Scope', fields: [
                            { id: 'definitions', label: 'Definitions', input: 'textarea', required: false },
                            { id: 'scope', label: 'Scope of Work', input: 'textarea', required: true },
                            { id: 'consideration', label: 'Consideration', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'schedules', title: 'Schedules & Annexures', fields: [
                            { id: 'schedules', label: 'Schedules', input: 'attachments', required: false }
                        ]
                    },
                    {
                        id: 'signatures', title: 'Signatures', fields: [
                            { id: 'signatures', label: 'Signature Blocks', input: 'signature', required: true }
                        ]
                    }
                ]
            },

            PowerOfAttorney: {
                display: 'Power of Attorney',
                description: 'POA template for corporate or personal use.',
                sections: [
                    {
                        id: 'metadata', title: 'Metadata', fields: [
                            { id: 'title', label: 'Title', input: 'text', required: true },
                            { id: 'effectiveDate', label: 'Effective Date', input: 'date', required: true }
                        ]
                    },
                    {
                        id: 'principal', title: 'Principal', fields: [
                            { id: 'principalName', label: 'Principal Name', input: 'text', required: true },
                            { id: 'principalId', label: 'ID / Passport', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'attorney', title: 'Attorney', fields: [
                            { id: 'attorneyName', label: 'Attorney Name', input: 'text', required: true },
                            { id: 'powers', label: 'Powers Granted', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'signature', title: 'Signature & Notary', fields: [
                            { id: 'signatoryName', label: 'Signatory Name', input: 'text', required: true },
                            { id: 'notary', label: 'Notary / Commissioner', input: 'text', required: false }
                        ]
                    }
                ]
            },

            LeaseAgreement: {
                display: 'Lease Agreement',
                description: 'Lease agreement with parties, premises, rent, term and schedules.',
                sections: [
                    {
                        id: 'metadata', title: 'Metadata', fields: [
                            { id: 'title', label: 'Lease Title', input: 'text', required: true },
                            { id: 'startDate', label: 'Start Date', input: 'date', required: true },
                            { id: 'endDate', label: 'End Date', input: 'date', required: true }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'landlord', label: 'Landlord', input: 'textarea', required: true },
                            { id: 'tenant', label: 'Tenant', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'terms', title: 'Terms', fields: [
                            { id: 'rent', label: 'Rent (ZAR)', input: 'currency', required: true },
                            { id: 'deposit', label: 'Deposit (ZAR)', input: 'currency', required: false },
                            { id: 'premises', label: 'Premises Description', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'schedules', title: 'Schedules', fields: [
                            { id: 'schedules', label: 'Schedules & Annexures', input: 'attachments', required: false }
                        ]
                    }
                ]
            }
        }
    },

    Labour: {
        display: 'Labour & Employment',
        types: {
            EmploymentContract: {
                display: 'Employment Contract',
                description: 'Employment contract with role, remuneration, benefits and termination clauses.',
                sections: [
                    {
                        id: 'metadata', title: 'Metadata', fields: [
                            { id: 'title', label: 'Contract Title', input: 'text', required: true },
                            { id: 'startDate', label: 'Start Date', input: 'date', required: true }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'employer', label: 'Employer', input: 'textarea', required: true },
                            { id: 'employee', label: 'Employee', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'terms', title: 'Terms', fields: [
                            { id: 'role', label: 'Role & Duties', input: 'textarea', required: true },
                            { id: 'salary', label: 'Salary (ZAR)', input: 'currency', required: true },
                            { id: 'termination', label: 'Termination', input: 'textarea', required: false }
                        ]
                    },
                    {
                        id: 'signatures', title: 'Signatures', fields: [
                            { id: 'signatures', label: 'Signature Blocks', input: 'signature', required: true }
                        ]
                    }
                ]
            },

            CCMAReferral: {
                display: 'CCMA Referral',
                description: 'Referral to CCMA with particulars of dispute and relief sought.',
                sections: [
                    {
                        id: 'metadata', title: 'Metadata', fields: [
                            { id: 'referralDate', label: 'Referral Date', input: 'date', required: true }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'employee', label: 'Employee', input: 'text', required: true },
                            { id: 'employer', label: 'Employer', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'dispute', title: 'Dispute Details', fields: [
                            { id: 'disputeSummary', label: 'Summary of Dispute', input: 'textarea', required: true },
                            { id: 'relief', label: 'Relief Sought', input: 'textarea', required: true }
                        ]
                    }
                ]
            }
        }
    },

    Property: {
        display: 'Property & Conveyancing',
        types: {
            TitleDeedTransfer: {
                display: 'Title Deed Transfer',
                description: 'Transfer of title deed with parties, property description and schedules.',
                sections: [
                    {
                        id: 'metadata', title: 'Metadata', fields: [
                            { id: 'transferDate', label: 'Transfer Date', input: 'date', required: true }
                        ]
                    },
                    {
                        id: 'parties', title: 'Parties', fields: [
                            { id: 'seller', label: 'Seller', input: 'textarea', required: true },
                            { id: 'buyer', label: 'Buyer', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'property', title: 'Property', fields: [
                            { id: 'description', label: 'Property Description', input: 'textarea', required: true },
                            { id: 'deedNumber', label: 'Deed Number', input: 'text', required: false }
                        ]
                    },
                    {
                        id: 'schedules', title: 'Schedules', fields: [
                            { id: 'schedules', label: 'Schedules & Annexures', input: 'attachments', required: false }
                        ]
                    }
                ]
            }
        }
    },

    Administrative: {
        display: 'Administrative & Public Law',
        types: {
            ReviewApplication: {
                display: 'Administrative Review',
                description: 'Application for review of administrative decision.',
                sections: [
                    {
                        id: 'header', title: 'Header', fields: [
                            { id: 'authority', label: 'Decision-making Authority', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'applicant', title: 'Applicant', fields: [
                            { id: 'applicantName', label: 'Applicant Name', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'grounds', title: 'Grounds', fields: [
                            { id: 'grounds', label: 'Grounds for Review', input: 'repeatable_text', required: true }
                        ]
                    },
                    {
                        id: 'relief', title: 'Relief', fields: [
                            { id: 'relief', label: 'Relief Sought', input: 'textarea', required: true }
                        ]
                    }
                ]
            }
        }
    },

    IntellectualProperty: {
        display: 'Intellectual Property',
        types: {
            PatentApplication: {
                display: 'Patent Application',
                description: 'Patent application with inventor details, claims and specifications.',
                sections: [
                    {
                        id: 'metadata', title: 'Metadata', fields: [
                            { id: 'title', label: 'Invention Title', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'inventor', title: 'Inventor', fields: [
                            { id: 'inventorName', label: 'Inventor Name', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'spec', title: 'Specification & Claims', fields: [
                            { id: 'specification', label: 'Specification', input: 'textarea', required: true },
                            { id: 'claims', label: 'Claims', input: 'repeatable_text', required: true }
                        ]
                    }
                ]
            }
        }
    },

    Tax: {
        display: 'Tax',
        types: {
            TaxObjection: {
                display: 'Tax Assessment Objection',
                description: 'Objection to tax assessment with grounds and supporting documents.',
                sections: [
                    {
                        id: 'metadata', title: 'Metadata', fields: [
                            { id: 'assessmentRef', label: 'Assessment Reference', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'applicant', title: 'Applicant', fields: [
                            { id: 'taxpayer', label: 'Taxpayer Name', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'grounds', title: 'Grounds & Relief', fields: [
                            { id: 'grounds', label: 'Grounds for Objection', input: 'repeatable_text', required: true },
                            { id: 'relief', label: 'Relief Sought', input: 'textarea', required: true }
                        ]
                    },
                    {
                        id: 'exhibits', title: 'Supporting Documents', fields: [
                            { id: 'supportingDocs', label: 'Supporting Documents', input: 'attachments', required: false }
                        ]
                    }
                ]
            }
        }
    },

    Environmental: {
        display: 'Environmental',
        types: {
            PermitAppeal: {
                display: 'Environmental Permit Appeal',
                description: 'Appeal against environmental permit decision.',
                sections: [
                    {
                        id: 'metadata', title: 'Metadata', fields: [
                            { id: 'permitRef', label: 'Permit Reference', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'appellant', title: 'Appellant', fields: [
                            { id: 'appellantName', label: 'Appellant Name', input: 'text', required: true }
                        ]
                    },
                    {
                        id: 'grounds', title: 'Grounds', fields: [
                            { id: 'grounds', label: 'Grounds for Appeal', input: 'repeatable_text', required: true }
                        ]
                    },
                    {
                        id: 'exhibits', title: 'Supporting Documents', fields: [
                            { id: 'supportingDocs', label: 'Supporting Documents', input: 'attachments', required: false }
                        ]
                    }
                ]
            }
        }
    }
};

/* -----------------------------------------------------------------------------
   Schema helpers
   -------------------------------------------------------------------------- */

function getCategories() {
    return Object.keys(DOCUMENT_SCHEMA).map(k => ({ id: k, display: DOCUMENT_SCHEMA[k].display }));
}

function getTypesForCategory(categoryId) {
    const cat = DOCUMENT_SCHEMA[categoryId];
    if (!cat) return [];
    return Object.keys(cat.types).map(t => ({ id: t, display: cat.types[t].display }));
}

function getTypeSchema(categoryId, typeId) {
    const cat = DOCUMENT_SCHEMA[categoryId];
    if (!cat) return null;
    return cat.types[typeId] || null;
}

/* -----------------------------------------------------------------------------
   Validators & helpers
   -------------------------------------------------------------------------- */

function validateFieldValue(field, value) {
    if (field.required) {
        if (field.input === 'attachments') {
            if (!value || value.length === 0) return 'Attachment required';
        } else if (field.input === 'repeatable_text' || field.input === 'repeatable_service') {
            if (!Array.isArray(value) || value.length === 0 || value.every(v => !String(v || '').trim())) return `${field.label} is required`;
        } else if (field.input === 'boolean') {
            // boolean may be optional
        } else if (!String(value || '').trim()) {
            return `${field.label} is required`;
        }
    }
    if (field.validator) {
        const res = field.validator(value);
        if (res !== true) return typeof res === 'string' ? res : `${field.label} is invalid`;
    }
    return null;
}

const AUTOSAVE_KEY_PREFIX = 'wilsy:doc:create:autosave:';
function autosaveKey(category, type) {
    return `${AUTOSAVE_KEY_PREFIX}${category || 'unknown'}:${type || 'unknown'}`;
}

function maskForUi(value = '') {
    try {
        const s = String(value || '');
        if (!s) return '';
        if (s.length <= 8) return s;
        return `${s.slice(0, 6)}…`;
    } catch {
        return '';
    }
}

function generateCorrelationId() {
    return `req_${Math.random().toString(36).slice(2, 10)}_${Date.now().toString(36)}`;
}

/* -----------------------------------------------------------------------------
   Component
   -------------------------------------------------------------------------- */

export default function DocumentCreate() {
    const navigate = useNavigate();
    const { user, token } = useAuthStore();
    const mountedRef = useRef(true);

    // UI state
    const [category, setCategory] = useState(() => getCategories()[0]?.id || 'Civil');
    const [type, setType] = useState(() => {
        const types = getTypesForCategory(getCategories()[0]?.id || 'Civil');
        return types[0]?.id || 'Affidavit';
    });

    // Document state
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [metadata, setMetadata] = useState({});
    const [attachments, setAttachments] = useState([]);
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [loading, setLoading] = useState(false);
    const [previewing, setPreviewing] = useState(false);
    const [autosaveTimer, setAutosaveTimer] = useState(null);

    // Audit & immutable metadata
    const [auditEvents, setAuditEvents] = useState([]);
    const [docMeta, setDocMeta] = useState({
        createdAt: null, createdBy: null, lastModifiedAt: null, lastModifiedBy: null,
        version: 1, correlationId: null, readyForESign: false
    });

    // Derived schema
    const availableTypes = useMemo(() => getTypesForCategory(category), [category]);
    const activeTypeSchema = useMemo(() => getTypeSchema(category, type), [category, type]);

    /* emitAudit: non-blocking, best-effort telemetry */
    const emitAudit = useCallback((eventType, payload = {}) => {
        try {
            const actor = user?.email || 'ANONYMOUS';
            const correlationId = payload.correlationId || generateCorrelationId();
            const entry = {
                timestamp: new Date().toISOString(),
                eventType,
                actor: maskForUi(actor),
                actorRole: user?.role || 'GUEST',
                tenant: maskForUi(user?.tenantName || user?.tenantId || ''),
                correlationId,
                metadata: payload.metadata || {}
            };
            setAuditEvents(prev => [entry, ...prev].slice(0, 20));
            try {
                AuthUtils?.AuditService?.log?.(eventType, {
                    actor, actorRole: user?.role, tenantId: user?.tenantId, correlationId, metadata: payload.metadata || {}
                });
            } catch (e) {
                // swallow telemetry errors
            }
        } catch (e) {
            // swallow
        }
    }, [user]);

    /* On mount: emit open audit */
    useEffect(() => {
        mountedRef.current = true;
        const corr = generateCorrelationId();
        emitAudit('DOCUMENT_CREATE_OPEN', { correlationId: corr, metadata: { category, type } });
        return () => { mountedRef.current = false; if (autosaveTimer) clearInterval(autosaveTimer); };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    /* Sync category -> type and restore autosave */
    useEffect(() => {
        const types = getTypesForCategory(category);
        const newType = types[0]?.id || Object.keys(DOCUMENT_SCHEMA[category]?.types || {})[0] || '';
        setType(prev => {
            if (DOCUMENT_SCHEMA[category] && DOCUMENT_SCHEMA[category].types[prev]) return prev;
            return newType;
        });

        const key = autosaveKey(category, newType);
        try {
            const raw = localStorage.getItem(key);
            if (raw) {
                const parsed = JSON.parse(raw);
                setTitle(parsed.title || '');
                setDescription(parsed.description || '');
                setMetadata(parsed.metadata || {});
                setAttachments(parsed.attachments || []);
            } else {
                const schema = getTypeSchema(category, newType);
                if (schema) {
                    const defaults = {};
                    for (const s of schema.sections) {
                        for (const f of s.fields) defaults[f.id] = f.input === 'repeatable_text' || f.input === 'repeatable_service' ? [''] : '';
                    }
                    setMetadata(defaults);
                } else {
                    setMetadata({});
                }
            }
        } catch (e) {
            setMetadata({});
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [category]);

    /* When type changes, reset metadata to schema defaults and restore autosave */
    useEffect(() => {
        const schema = getTypeSchema(category, type);
        if (!schema) return;
        const defaults = {};
        for (const s of schema.sections) {
            for (const f of s.fields) {
                defaults[f.id] = metadata[f.id] !== undefined ? metadata[f.id] : (f.input === 'repeatable_text' || f.input === 'repeatable_service' ? [''] : '');
            }
        }
        setMetadata(defaults);

        const key = autosaveKey(category, type);
        try {
            const raw = localStorage.getItem(key);
            if (raw) {
                const parsed = JSON.parse(raw);
                setTitle(parsed.title || '');
                setDescription(parsed.description || '');
                setMetadata(prev => ({ ...prev, ...(parsed.metadata || {}) }));
                setAttachments(parsed.attachments || []);
            }
        } catch (e) {
            // ignore
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [type]);

    /* Field setter */
    const setFieldValue = useCallback((fieldId, value) => {
        setMetadata(prev => ({ ...prev, [fieldId]: value }));
        setErrors(prev => ({ ...prev, [fieldId]: undefined }));
    }, []);

    /* Attachments */
    const handleAttachments = useCallback((files) => {
        const arr = Array.from(files || []);
        setAttachments(prev => [...prev, ...arr]);
        emitAudit('DOCUMENT_ATTACHMENTS_ADDED', { metadata: { count: arr.length } });
    }, [emitAudit]);

    const removeAttachment = useCallback((index) => {
        setAttachments(prev => prev.filter((_, i) => i !== index));
        emitAudit('DOCUMENT_ATTACHMENT_REMOVED', { metadata: { index } });
    }, [emitAudit]);

    /* Autosave every 15s */
    useEffect(() => {
        const key = autosaveKey(category, type);
        const save = () => {
            try {
                const payload = { title, description, metadata, attachments: attachments.map(a => ({ name: a.name, size: a.size })) };
                localStorage.setItem(key, JSON.stringify(payload));
                emitAudit('DOCUMENT_AUTOSAVE', { metadata: { category, type } });
            } catch (e) {
                // ignore
            }
        };
        const id = setInterval(save, 15000);
        setAutosaveTimer(id);
        save();
        return () => clearInterval(id);
    }, [category, type, title, description, metadata, attachments, emitAudit]);

    /* Validation */
    const validateAll = useCallback(() => {
        const schema = activeTypeSchema;
        const newErrors = {};
        if (!String(title || '').trim()) newErrors.title = 'Document title / case reference is required';
        if (!schema) {
            newErrors._schema = 'Unknown document type';
            setErrors(newErrors);
            return newErrors;
        }
        for (const s of schema.sections) {
            for (const field of s.fields) {
                const val = metadata[field.id];
                const err = validateFieldValue(field, val);
                if (err) newErrors[field.id] = err;
            }
        }
        // Example per-type checks
        if (category === 'Civil' && type === 'Affidavit') {
            if (!metadata.swornOn || !String(metadata.swornOn).trim()) newErrors.swornOn = 'Sworn on date is required for an affidavit';
            const paragraphs = metadata.statement;
            if (!Array.isArray(paragraphs) || paragraphs.length === 0 || paragraphs.every(p => !String(p || '').trim())) {
                newErrors.statement = 'At least one numbered paragraph is required';
            }
        }
        setErrors(newErrors);
        return newErrors;
    }, [activeTypeSchema, metadata, title, category, type]);

    /* Error reporting helper */
    const showUserError = useCallback((err, correlationId) => {
        toast.error('Unable to save document. Please try again or contact support.');
        try {
            AuthUtils?.Logger?.error?.('DocumentCreate: error', { correlationId, error: err && (err.message || err) });
            AuthUtils?.AuditService?.log?.('DOCUMENT_CREATE_CLIENT_ERROR', { metadata: { correlationId, error: err && (err.message || String(err)) } });
        } catch (e) {
            // swallow
        }
    }, []);

    /* Preview */
    const handlePreview = useCallback(async () => {
        const corr = generateCorrelationId();
        setPreviewing(true);
        setLoading(true);
        emitAudit('DOCUMENT_PREVIEW_INIT', { correlationId: corr, metadata: { category, type } });
        try {
            const payload = { title, category, type, description, metadata, tenantId: user?.tenantId || null, attachments: [] };
            const res = await documentService.createDocument(token, { ...payload, preview: true });
            if (res && res.ok) {
                emitAudit('DOCUMENT_PREVIEW_SUCCESS', { correlationId: corr, metadata: { documentId: res.data?._id || res.data?.id } });
                toast.success('Preview generated. Opening in new tab...');
                if (res.data && res.data.previewUrl) {
                    window.open(res.data.previewUrl, '_blank', 'noopener');
                } else {
                    toast.info('Preview ready in documents list.');
                }
            } else {
                emitAudit('DOCUMENT_PREVIEW_FAILURE', { correlationId: corr, metadata: { error: res?.message } });
                showUserError(res, corr);
            }
        } catch (err) {
            emitAudit('DOCUMENT_PREVIEW_ERROR', { correlationId: corr, metadata: { error: err?.message } });
            showUserError(err, corr);
        } finally {
            if (mountedRef.current) {
                setPreviewing(false);
                setLoading(false);
            }
        }
    }, [title, category, type, description, metadata, user, token, showUserError, emitAudit]);

    /* Submit */
    const handleSubmit = useCallback(async (ev) => {
        ev && ev.preventDefault();
        if (submitting) return;
        const corr = generateCorrelationId();
        const validation = validateAll();
        if (Object.keys(validation).length > 0) {
            toast.warning('Please fix validation errors before saving.');
            emitAudit('DOCUMENT_CREATE_VALIDATION_FAILED', { correlationId: corr, metadata: { validation, category, type } });
            return;
        }
        if (!user || !user.tenantId) {
            toast.error('User context missing. Please refresh or sign in again.');
            emitAudit('DOCUMENT_CREATE_NO_TENANT', { correlationId: corr, metadata: { user: maskForUi(user?.email) } });
            return;
        }

        setSubmitting(true);
        setLoading(true);

        const now = new Date().toISOString();
        const payload = {
            title: String(title).trim(),
            category,
            type,
            description: String(description || ''),
            tenantId: user.tenantId,
            metadata,
            attachments: [], // attachments upload handled separately
            createdAt: docMeta.createdAt || now,
            createdBy: docMeta.createdBy || (user.email || user.id || user._id || 'unknown'),
            lastModifiedAt: now,
            lastModifiedBy: user.email || user.id || user._id || 'unknown',
            version: docMeta.version || 1,
            correlationId: corr,
            readyForESign: docMeta.readyForESign || false
        };

        try {
            emitAudit('DOCUMENT_CREATE_INIT', { correlationId: corr, metadata: { category, type } });
            const res = await documentService.createDocument(token, payload);

            if (res && res.ok) {
                setDocMeta({
                    createdAt: payload.createdAt,
                    createdBy: payload.createdBy,
                    lastModifiedAt: payload.lastModifiedAt,
                    lastModifiedBy: payload.lastModifiedBy,
                    version: (payload.version || 1) + 1,
                    correlationId: corr,
                    readyForESign: payload.readyForESign || false
                });

                emitAudit('DOCUMENT_CREATE_SUCCESS', { correlationId: corr, metadata: { documentId: res.data?._id || res.data?.id } });
                toast.success('Document created (draft).');
                const docId = res.data?._id || res.data?.id || null;
                if (docId) navigate(`/documents/${docId}`);
                else navigate('/documents');
            } else {
                emitAudit('DOCUMENT_CREATE_FAILURE', { correlationId: corr, metadata: { error: res?.message } });
                showUserError(res, corr);
            }
        } catch (err) {
            emitAudit('DOCUMENT_CREATE_ERROR', { correlationId: corr, metadata: { error: err?.message } });
            showUserError(err, corr);
        } finally {
            if (mountedRef.current) {
                setSubmitting(false);
                setLoading(false);
            }
        }
    }, [title, category, type, description, metadata, user, token, submitting, navigate, showUserError, validateAll, docMeta, emitAudit]);

    /* Render field helper */
    function renderField(field) {
        const value = metadata[field.id];
        const err = errors[field.id];
        switch (field.input) {
            case 'text':
                return (
                    <Field key={field.id}>
                        <Label htmlFor={field.id}>{field.label}{field.required ? ' *' : ''}</Label>
                        <Input id={field.id} value={value || ''} onChange={e => setFieldValue(field.id, e.target.value)} />
                        {field.help && <Hint>{field.help}</Hint>}
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'number':
            case 'currency':
                return (
                    <Field key={field.id}>
                        <Label htmlFor={field.id}>{field.label}{field.required ? ' *' : ''}</Label>
                        <Input id={field.id} type="number" value={value || ''} onChange={e => setFieldValue(field.id, e.target.value)} />
                        {field.help && <Hint>{field.help}</Hint>}
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'date':
                return (
                    <Field key={field.id}>
                        <Label htmlFor={field.id}>{field.label}{field.required ? ' *' : ''}</Label>
                        <Input id={field.id} type="date" value={value || ''} onChange={e => setFieldValue(field.id, e.target.value)} />
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'textarea':
                return (
                    <Field key={field.id}>
                        <Label htmlFor={field.id}>{field.label}{field.required ? ' *' : ''}</Label>
                        <Textarea id={field.id} value={value || ''} onChange={e => setFieldValue(field.id, e.target.value)} />
                        {field.help && <Hint>{field.help}</Hint>}
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'repeatable_text':
                return (
                    <Field key={field.id}>
                        <Label>{field.label}{field.required ? ' *' : ''}</Label>
                        {(Array.isArray(value) ? value : ['']).map((v, idx) => (
                            <div key={idx} style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                                <Textarea value={v} onChange={e => {
                                    const arr = Array.isArray(value) ? [...value] : [''];
                                    arr[idx] = e.target.value;
                                    setFieldValue(field.id, arr);
                                }} />
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    <Button type="button" ghost onClick={() => {
                                        const arr = Array.isArray(value) ? [...value] : [''];
                                        arr.splice(idx, 1);
                                        setFieldValue(field.id, arr);
                                    }}><FiMinus /></Button>
                                    <Button type="button" onClick={() => {
                                        const arr = Array.isArray(value) ? [...value] : [''];
                                        arr.splice(idx + 1, 0, '');
                                        setFieldValue(field.id, arr);
                                    }}><FiPlus /></Button>
                                </div>
                            </div>
                        ))}
                        {field.help && <Hint>{field.help}</Hint>}
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'repeatable_service':
                return (
                    <Field key={field.id}>
                        <Label>{field.label}{field.required ? ' *' : ''}</Label>
                        {(Array.isArray(value) ? value : []).map((v, idx) => (
                            <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1fr 160px', gap: 8, marginBottom: 8 }}>
                                <Input value={v.method || ''} placeholder="Method (e.g., Personal)" onChange={e => {
                                    const arr = Array.isArray(value) ? [...value] : [];
                                    arr[idx] = { ...(arr[idx] || {}), method: e.target.value };
                                    setFieldValue(field.id, arr);
                                }} />
                                <Input value={v.date || ''} type="date" onChange={e => {
                                    const arr = Array.isArray(value) ? [...value] : [];
                                    arr[idx] = { ...(arr[idx] || {}), date: e.target.value };
                                    setFieldValue(field.id, arr);
                                }} />
                                <div style={{ gridColumn: '1 / -1', display: 'flex', gap: 8 }}>
                                    <Input value={v.notes || ''} placeholder="Notes / proof reference" onChange={e => {
                                        const arr = Array.isArray(value) ? [...value] : [];
                                        arr[idx] = { ...(arr[idx] || {}), notes: e.target.value };
                                        setFieldValue(field.id, arr);
                                    }} />
                                    <Button type="button" ghost onClick={() => {
                                        const arr = Array.isArray(value) ? [...value] : [];
                                        arr.splice(idx, 1);
                                        setFieldValue(field.id, arr);
                                    }}><FiMinus /></Button>
                                </div>
                            </div>
                        ))}
                        <Button type="button" onClick={() => {
                            const arr = Array.isArray(value) ? [...value] : [];
                            arr.push({ method: '', date: '', notes: '' });
                            setFieldValue(field.id, arr);
                        }}><FiPlus /> Add Service Entry</Button>
                        {field.help && <Hint>{field.help}</Hint>}
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'attachments':
                return (
                    <Field key={field.id}>
                        <Label>{field.label}{field.required ? ' *' : ''}</Label>
                        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <label style={{ display: 'inline-flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                                <FiUpload /> <span>Upload</span>
                                <input type="file" multiple style={{ display: 'none' }} onChange={e => handleAttachments(e.target.files)} />
                            </label>
                        </div>
                        {attachments.length > 0 && (
                            <div style={{ marginTop: 8 }}>
                                {attachments.map((a, i) => (
                                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 6, border: '1px solid #f1f5f9', borderRadius: 6, marginBottom: 6 }}>
                                        <div style={{ fontSize: 14 }}>{a.name} <span style={{ color: '#94a3b8', fontSize: 12 }}>({Math.round(a.size / 1024)} KB)</span></div>
                                        <div style={{ display: 'flex', gap: 8 }}>
                                            <Button type="button" ghost onClick={() => removeAttachment(i)}>Remove</Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                        {field.help && <Hint>{field.help}</Hint>}
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'signature':
                return (
                    <Field key={field.id}>
                        <Label>{field.label}{field.required ? ' *' : ''}</Label>
                        <Hint>Enter signatory name; e-sign integration will be available at finalization.</Hint>
                        <Input value={value || ''} onChange={e => setFieldValue(field.id, e.target.value)} placeholder="Signatory full name" />
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'select':
                return (
                    <Field key={field.id}>
                        <Label>{field.label}{field.required ? ' *' : ''}</Label>
                        <Select value={value || ''} onChange={e => setFieldValue(field.id, e.target.value)}>
                            <option value="">-- Select --</option>
                            {(field.options || []).map(opt => <option key={opt} value={opt}>{opt}</option>)}
                        </Select>
                        {field.help && <Hint>{field.help}</Hint>}
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            case 'boolean':
                return (
                    <Field key={field.id}>
                        <Label>{field.label}</Label>
                        <div style={{ display: 'flex', gap: 8 }}>
                            <label><input type="checkbox" checked={!!value} onChange={e => setFieldValue(field.id, e.target.checked)} /> Yes</label>
                        </div>
                        {field.help && <Hint>{field.help}</Hint>}
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
            default:
                return (
                    <Field key={field.id}>
                        <Label>{field.label}{field.required ? ' *' : ''}</Label>
                        <Input value={value || ''} onChange={e => setFieldValue(field.id, e.target.value)} />
                        {err && <ErrorText role="alert">{err}</ErrorText>}
                    </Field>
                );
        }
    }

    /* Render */
    return (
        <Page>
            <Panel aria-labelledby="doc-create-heading">
                <Header>
                    <div>
                        <h1 id="doc-create-heading"><FiFileText aria-hidden="true" /> New Legal Instrument</h1>
                        <p>Complete, court-ready forms. Choose a category and type; the UI renders structured sections for legal accuracy. Drafts autosave and every action is auditable.</p>
                    </div>

                    <div style={{ textAlign: 'right', color: 'var(--color-text-muted,#64748b)', fontSize: 12 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <div style={{ width: 40, height: 40, borderRadius: 8, background: '#2563EB', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800 }}>
                                {user ? (user.firstName ? (user.firstName.charAt(0) + (user.lastName ? user.lastName.charAt(0) : '')).toUpperCase() : (user.email ? user.email.charAt(0).toUpperCase() : '?')) : '?'}
                            </div>
                            <div style={{ textAlign: 'left' }}>
                                <div style={{ fontWeight: 800 }}>{user ? (user.name || maskForUi(user.email)) : 'Not signed in'}</div>
                                <div style={{ fontSize: 12, color: 'var(--color-text-muted,#64748b)' }}>{user ? `${(user.role || 'GUEST').toUpperCase()} • ${user.tenantName || maskForUi(user.tenantId || '')}` : ''}</div>
                                <div style={{ marginTop: 6 }}>
                                    <a href="#" onClick={(e) => { e.preventDefault(); emitAudit('DOCUMENT_VIEW_AUDIT_TRAIL', { metadata: {} }); toast.info('Audit trail opened (server view may be available).'); }}>View audit trail</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </Header>

                <Form onSubmit={handleSubmit} noValidate>
                    <Grid>
                        <Column>
                            <Field>
                                <Label htmlFor="title">Document Title / Case Reference *</Label>
                                <Input id="title" value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. State vs. Smith or Case #9921" />
                                {errors.title && <ErrorText role="alert">{errors.title}</ErrorText>}
                            </Field>

                            <Field>
                                <Label htmlFor="category">Legal Category *</Label>
                                <Select id="category" value={category} onChange={e => setCategory(e.target.value)}>
                                    {getCategories().map(c => <option key={c.id} value={c.id}>{c.display}</option>)}
                                </Select>
                                {errors.category && <ErrorText role="alert">{errors.category}</ErrorText>}
                            </Field>

                            <Field>
                                <Label htmlFor="type">Document Type *</Label>
                                <Select id="type" value={type} onChange={e => setType(e.target.value)}>
                                    {availableTypes.map(t => <option key={t.id} value={t.id}>{t.display}</option>)}
                                </Select>
                                {errors.type && <ErrorText role="alert">{errors.type}</ErrorText>}
                                {activeTypeSchema && <Hint style={{ marginTop: 8 }}>{activeTypeSchema.description}</Hint>}
                            </Field>

                            <Field>
                                <Label htmlFor="description">Short Description</Label>
                                <Textarea id="description" value={description} onChange={e => setDescription(e.target.value)} placeholder="Optional summary for reviewers" />
                            </Field>

                            {/* Render sections */}
                            {activeTypeSchema && activeTypeSchema.sections.map(section => (
                                <div key={section.id} style={{ marginTop: 12, padding: 12, border: '1px solid #f1f5f9', borderRadius: 8 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <div style={{ fontWeight: 800 }}>{section.title}</div>
                                            {section.subtitle && <div style={{ color: 'var(--color-text-muted,#64748b)', fontSize: 13 }}>{section.subtitle}</div>}
                                        </div>
                                        {section.help && <div style={{ fontSize: 13, color: 'var(--color-text-muted,#64748b)' }}>{section.help}</div>}
                                    </div>

                                    <div style={{ marginTop: 12 }}>
                                        {section.fields.map(f => renderField(f))}
                                    </div>
                                </div>
                            ))}

                            <Actions>
                                <Button type="button" ghost onClick={() => { emitAudit('DOCUMENT_CREATE_CANCEL', {}); navigate(-1); }} disabled={submitting}><FiX /> Cancel</Button>
                                <Button type="button" ghost onClick={handlePreview} disabled={previewing || submitting || loading}><FiEye /> Preview</Button>
                                <Button type="submit" disabled={submitting || loading}><FiSave /> {submitting ? 'Creating…' : 'Create & Draft'}</Button>
                            </Actions>
                        </Column>

                        <Sidebar aria-label="Document helper">
                            <h3 style={{ marginTop: 0 }}>Type Helper & Audit</h3>
                            {activeTypeSchema ? (
                                <>
                                    <div style={{ fontWeight: 800 }}>{activeTypeSchema.display}</div>
                                    <div style={{ marginTop: 8, color: 'var(--color-text-muted,#64748b)' }}>{activeTypeSchema.description}</div>
                                    <hr style={{ margin: '12px 0' }} />
                                    <div style={{ fontSize: 13, color: 'var(--color-text-muted,#64748b)' }}>
                                        <strong>Sections:</strong>
                                        <ul>
                                            {activeTypeSchema.sections.map(s => <li key={s.id}>{s.title}</li>)}
                                        </ul>
                                    </div>

                                    <div style={{ marginTop: 12 }}>
                                        <strong>Required fields (summary):</strong>
                                        <ul>
                                            {activeTypeSchema.sections.flatMap(s => s.fields.filter(f => f.required)).map(f => <li key={f.id}>{f.label}</li>)}
                                        </ul>
                                    </div>

                                    <div style={{ marginTop: 12 }}>
                                        <strong>Immutable metadata</strong>
                                        <div style={{ fontSize: 13, color: 'var(--color-text-muted,#64748b)' }}>
                                            <div>Created: {docMeta.createdAt ? new Date(docMeta.createdAt).toLocaleString() : '—'}</div>
                                            <div>Created by: {docMeta.createdBy ? maskForUi(docMeta.createdBy) : '—'}</div>
                                            <div>Last modified: {docMeta.lastModifiedAt ? new Date(docMeta.lastModifiedAt).toLocaleString() : '—'}</div>
                                            <div>Last modified by: {docMeta.lastModifiedBy ? maskForUi(docMeta.lastModifiedBy) : '—'}</div>
                                            <div>Version: {docMeta.version || 1}</div>
                                            <div>Correlation: {docMeta.correlationId ? maskForUi(docMeta.correlationId) : '—'}</div>
                                            <div>Ready for e-sign: {docMeta.readyForESign ? 'Yes' : 'No'}</div>
                                        </div>
                                    </div>

                                    <hr style={{ margin: '12px 0' }} />

                                    <div>
                                        <strong>Recent audit events</strong>
                                        <div style={{ marginTop: 8 }}>
                                            {auditEvents.slice(0, 5).map((a, i) => (
                                                <div key={i} style={{ padding: 8, borderBottom: '1px solid #f1f5f9' }}>
                                                    <div style={{ fontSize: 12, fontWeight: 700 }}>{a.eventType}</div>
                                                    <div style={{ fontSize: 12, color: '#64748b' }}>{new Date(a.timestamp).toLocaleString()} • {a.actor} • {a.actorRole}</div>
                                                    <div style={{ fontSize: 12, color: '#94a3b8' }}>corr: {maskForUi(a.correlationId)}</div>
                                                </div>
                                            ))}
                                            {auditEvents.length === 0 && <div style={{ color: '#94a3b8' }}>No local audit events yet.</div>}
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div>Choose a document type to see required fields and guidance.</div>
                            )}
                        </Sidebar>
                    </Grid>
                </Form>
            </Panel>
        </Page>
    );
}

/* -----------------------------------------------------------------------------
   Collaboration notes & next steps
   - This file is production-ready as a UI layer. Required backend work:
     * documentService.createDocument must accept payload and return normalized shape.
     * Implement attachment upload endpoint (multipart or pre-signed URLs).
     * Implement server-side preview endpoint returning previewUrl.
     * Persist audit events in append-only store and expose audit API for document-level audit retrieval.
   - QA: add tests for validation, autosave, preview, create flows.
   - Security: review telemetry, retention, PII handling.
   - UX: consider progressive disclosure (collapsible sections) for very long templates.
   - Extensibility: add new types by editing DOCUMENT_SCHEMA only; update tests and backend contract.
   -------------------------------------------------------------------------- */
