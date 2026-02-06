/*
 * File: src/features/admin/pages/AuditDetail.jsx
 * STATUS: EPITOME | FORENSIC DEEP-DIVE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Provides an exhaustive forensic breakdown of a specific system event. 
 * Essential for legal accountability and chain-of-custody verification.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - COMPLIANCE: Tracks 'Findings' and 'Corrective Actions' for ISO/POPIA audits.
 * - DEVOPS: Displays raw metadata and transition history for debugging.
 * - UI/UX: Uses card-based grouping for multi-dimensional data.
 * -----------------------------------------------------------------------------
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import {
    ChevronLeft,
    ShieldCheck,
    History,
    Terminal,
    User,
    Clock,
    AlertCircle
} from 'lucide-react';

// --- BRAIN & ENGINE ---
import api from '../../../api/axios';
import PageTransition from '../../../components/layout/PageTransition';

// --- STYLED ARCHITECTURE ---

const DetailWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;

  button {
    background: white; border: 1px solid #E2E8F0; padding: 10px;
    border-radius: 12px; cursor: pointer; color: #64748B;
    display: flex; align-items: center; justify-content: center;
    &:hover { border-color: #0F172A; color: #0F172A; }
  }

  .title-block {
    h1 { font-size: 1.5rem; font-weight: 800; color: #0F172A; margin: 0; }
    span { font-size: 0.85rem; color: #64748B; font-family: monospace; }
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  @media (max-width: 1024px) { grid-template-columns: 1fr; }
`;

const Card = styled.div`
  background: white; border-radius: 20px; border: 1px solid #E2E8F0;
  padding: 24px; margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);

  .card-label { 
    display: flex; align-items: center; gap: 8px;
    font-size: 0.9rem; font-weight: 800; color: #0F172A; margin-bottom: 20px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
`;

const MetaDataBox = styled.pre`
  background: #0F172A; color: #38BDF8; padding: 20px;
  border-radius: 12px; font-family: 'Fira Code', monospace;
  font-size: 0.8rem; overflow-x: auto; line-height: 1.5;
`;

const InfoRow = styled.div`
  display: flex; justify-content: space-between; padding: 12px 0;
  border-bottom: 1px solid #F1F5F9;
  &:last-child { border-bottom: none; }
  .label { color: #64748B; font-weight: 600; font-size: 0.85rem; }
  .value { color: #0F172A; font-weight: 700; font-size: 0.85rem; }
`;

const FindingItem = styled.div`
  padding: 16px; border-radius: 12px; background: #F8FAFC;
  border-left: 4px solid ${props => props.$resolved ? '#10B981' : '#EF4444'};
  margin-bottom: 12px;
  h4 { margin: 0 0 4px 0; font-size: 0.9rem; color: #0F172A; }
  p { margin: 0; font-size: 0.8rem; color: #64748B; }
`;

// -----------------------------------------------------------------------------
// COMPONENT LOGIC
// -----------------------------------------------------------------------------

export default function AuditDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [audit, setAudit] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAudit = async () => {
            try {
                const res = await api.get(`/audits/${id}`);
                setAudit(res.data);
            } catch (err) {
                console.error('Forensic Detail Retrieval Failed', err);
            } finally {
                setLoading(false);
            }
        };
        fetchAudit();
    }, [id]);

    if (loading) return <div className="p-20 text-center">Decrypting Vault Record...</div>;
    if (!audit) return <div className="p-20 text-center">Record Expunged or Non-Existent.</div>;

    return (
        <PageTransition>
            <DetailWrapper>
                <Header>
                    <button onClick={() => navigate(-1)}><ChevronLeft size={20} /></button>
                    <div className="title-block">
                        <h1>{audit.auditType} Report</h1>
                        <span>ID: {audit.auditCode}</span>
                    </div>
                </Header>

                <Grid>
                    <div className="main-content">
                        {/* 1. PRIMARY EVIDENCE */}
                        <Card>
                            <div className="card-label"><ShieldCheck size={18} color="#2563EB" /> Core Event Metadata</div>
                            <InfoRow><div className="label">Description</div><div className="value">{audit.description}</div></InfoRow>
                            <InfoRow><div className="label">Status</div><div className="value">{audit.status}</div></InfoRow>
                            <InfoRow><div className="label">Resource Path</div><div className="value">{audit.resourcePath || 'Root System'}</div></InfoRow>
                        </Card>

                        {/* 2. FORENSIC FINDINGS */}
                        <Card>
                            <div className="card-label"><AlertCircle size={18} color="#EF4444" /> Investigative Findings</div>
                            {audit.findings?.length > 0 ? audit.findings.map((f, i) => (
                                <FindingItem key={i} $resolved={f.resolved}>
                                    <h4>{f.description}</h4>
                                    <p>Severity: {f.severity} | Action: {f.correctiveAction || 'None Taken'}</p>
                                </FindingItem>
                            )) : <p style={{ color: '#94A3B8', fontSize: '0.85rem' }}>No high-severity findings for this record.</p>}
                        </Card>

                        {/* 3. RAW SYSTEM LOGS */}
                        <Card>
                            <div className="card-label"><Terminal size={18} color="#0F172A" /> Raw Transaction Data</div>
                            <MetaDataBox>
                                {JSON.stringify(audit.metadata || { message: "No extended metadata captured" }, null, 2)}
                            </MetaDataBox>
                        </Card>
                    </div>

                    <div className="sidebar-content">
                        {/* 4. ENTITY INFO */}
                        <Card>
                            <div className="card-label"><User size={18} color="#2563EB" /> Agent Identity</div>
                            <InfoRow><div className="label">Practitioner</div><div className="value">{audit.createdBy?.name || 'System'}</div></InfoRow>
                            <InfoRow><div className="label">Email</div><div className="value">{audit.createdBy?.email || 'N/A'}</div></InfoRow>
                            <InfoRow><div className="label">IP Address</div><div className="value">{audit.ipAddress || 'Internal'}</div></InfoRow>
                        </Card>

                        {/* 5. TIMELINE */}
                        <Card>
                            <div className="card-label"><Clock size={18} color="#2563EB" /> Timeline</div>
                            <InfoRow><div className="label">Captured</div><div className="value">{new Date(audit.createdAt).toLocaleString()}</div></InfoRow>
                            <InfoRow><div className="label">Last Modified</div><div className="value">{new Date(audit.updatedAt).toLocaleString()}</div></InfoRow>
                        </Card>

                        {/* 6. CHAIN OF CUSTODY */}
                        <Card>
                            <div className="card-label"><History size={18} color="#2563EB" /> Revision History</div>
                            {audit.history?.map((h, i) => (
                                <div key={i} style={{ fontSize: '0.75rem', padding: '10px 0', borderBottom: '1px solid #F1F5F9' }}>
                                    <div style={{ fontWeight: 800, color: '#0F172A' }}>{h.action}</div>
                                    <div style={{ color: '#64748B' }}>{new Date(h.date).toLocaleDateString()} • {h.reason}</div>
                                </div>
                            ))}
                        </Card>
                    </div>
                </Grid>
            </DetailWrapper>
        </PageTransition>
    );
}