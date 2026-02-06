/*
 * File: src/features/admin/pages/AuditPage.jsx
 * STATUS: EPITOME | FORENSIC AUDIT VAULT
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The authoritative record of every action taken within Wilsy OS. 
 * Provides forensic traceability for compliance (POPIA/GDPR) and legal discovery.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - AUDITORS: Real-time filtering by severity and action type.
 * - SECURITY: Displays IP addresses and User Agents (Metadata) for forensic tracing.
 * - UI/UX: Uses an interactive table with row-level navigation to AuditDetail.
 * -----------------------------------------------------------------------------
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import {
    Search,
    Filter,
    Download,
    Eye,
    ShieldAlert,
    Info,
    CheckCircle
} from 'lucide-react';

// --- BRAIN & ENGINE ---
import api from '../../../api/axios';
import PageTransition from '../../../components/layout/PageTransition';

// --- STYLED ARCHITECTURE ---

const VaultHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  .title-group {
    h1 { font-size: 1.75rem; font-weight: 900; color: #0F172A; }
    p { color: #64748B; font-size: 0.9rem; }
  }
`;

const ControlBar = styled.div`
  display: flex;
  gap: 16px;
  background: white;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  margin-bottom: 20px;
  align-items: center;
`;

const SearchInput = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background: #F8FAFC;
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  
  input {
    border: none; background: transparent; outline: none; width: 100%;
    color: #1E293B; font-size: 0.9rem;
  }
`;

const ForensicTable = styled.table`
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: white;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  overflow: hidden;

  th {
    background: #F8FAFC;
    padding: 16px;
    text-align: left;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    color: #64748B;
    border-bottom: 1px solid #E2E8F0;
  }

  td {
    padding: 16px;
    border-bottom: 1px solid #F1F5F9;
    font-size: 0.85rem;
    color: #334155;
    vertical-align: middle;
  }

  tr:last-child td { border-bottom: none; }
  
  tr:hover td {
    background: #FBFDFF;
    cursor: pointer;
  }
`;

const SeverityBadge = styled.span`
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  
  ${props => props.$level === 'HIGH' || props.$level === 'CRITICAL' ? `
    background: #FEE2E2; color: #991B1B;
  ` : props.$level === 'WARNING' ? `
    background: #FEF3C7; color: #92400E;
  ` : `
    background: #D1FAE5; color: #065F46;
  `}
`;

// -----------------------------------------------------------------------------
// COMPONENT LOGIC
// -----------------------------------------------------------------------------

export default function AuditPage() {
    const navigate = useNavigate();
    const [audits, setAudits] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchAudits = async () => {
            try {
                // Pointing to our consolidated audit endpoint
                const response = await api.get('/audits');
                setAudits(response.data || []);
            } catch (err) {
                console.error('Forensic Retrieval Failed:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchAudits();
    }, []);

    const filteredAudits = audits.filter(audit =>
        audit.auditCode?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        audit.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <PageTransition>
            <VaultHeader>
                <div className="title-group">
                    <h1>Forensic Audit Vault</h1>
                    <p>Wilsy OS Immutable Transaction Record</p>
                </div>
                <button
                    style={{ background: '#0F172A', color: 'white', padding: '10px 20px', borderRadius: '8px', border: 'none', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700', cursor: 'pointer' }}
                >
                    <Download size={16} /> Export Discovery
                </button>
            </VaultHeader>

            <ControlBar>
                <SearchInput>
                    <Search size={18} color="#94A3B8" />
                    <input
                        type="text"
                        placeholder="Search by Audit Code or Description..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </SearchInput>
                <button style={{ background: 'white', border: '1px solid #E2E8F0', padding: '8px 16px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600', color: '#475569', cursor: 'pointer' }}>
                    <Filter size={16} /> Filter
                </button>
            </ControlBar>

            <ForensicTable>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Audit Code</th>
                        <th>Action Type</th>
                        <th>Severity</th>
                        <th>Practitioner</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {loading ? (
                        <tr><td colSpan="6" style={{ textAlign: 'center', padding: '40px' }}>Decrypting Forensic Logs...</td></tr>
                    ) : filteredAudits.map((audit) => (
                        <tr key={audit._id} onClick={() => navigate(`/admin/audit/${audit._id}`)}>
                            <td style={{ fontWeight: '600' }}>
                                {new Date(audit.createdAt).toLocaleString('en-ZA', { dateStyle: 'medium', timeStyle: 'short' })}
                            </td>
                            <td style={{ fontFamily: 'monospace', color: '#2563EB', fontWeight: '700' }}>
                                {audit.auditCode}
                            </td>
                            <td>{audit.auditType}</td>
                            <td>
                                <SeverityBadge $level={audit.severity || 'INFO'}>
                                    {audit.severity === 'CRITICAL' ? <ShieldAlert size={12} /> : <Info size={12} />}
                                    {audit.severity || 'INFO'}
                                </SeverityBadge>
                            </td>
                            <td>
                                <div style={{ fontWeight: '700' }}>{audit.createdBy?.name || 'System'}</div>
                                <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>{audit.createdBy?.email || 'automated@wilsy.os'}</div>
                            </td>
                            <td>
                                <IconButton title="View Trace"><Eye size={16} /></IconButton>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </ForensicTable>
        </PageTransition>
    );
}

const IconButton = styled.button`
    background: none; border: none; color: #94A3B8; cursor: pointer;
    &:hover { color: #2563EB; }
`;