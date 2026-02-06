/*
 * File: src/features/admin/pages/UserList.jsx
 * STATUS: EPITOME | ACCESS CONTROL CENTER
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The Gatekeeper interface. Manages system access, role delegation, 
 * and security status (Active/Suspended) for all personnel.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - SECURITY: Only accessible by SUPER_ADMIN or ADMIN roles.
 * - UX: Quick-toggle for user suspension (Instant Lockout).
 * - BACKEND: Syncs with /api/users via socket updates.
 * -----------------------------------------------------------------------------
 */

'use client';

import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import {
    Users,
    UserPlus,
    Search,
    Shield,
    Briefcase,
    MoreVertical,
    Lock,
    Unlock,
    Mail,
    CheckCircle,
    XCircle
} from 'lucide-react';
import { toast } from 'react-toastify';

// --- BRAIN & ENGINE ---
import api from '../../../api/axios';
import PageTransition from '../../../components/layout/PageTransition';

// --- STYLED ARCHITECTURE ---

const PageContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;

  .title-group {
    h1 { font-size: 1.75rem; font-weight: 900; color: #0F172A; margin: 0; }
    p { color: #64748B; font-size: 0.95rem; margin-top: 4px; }
  }
`;

const ControlBar = styled.div`
  display: flex;
  gap: 16px;
  background: white;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  margin-bottom: 24px;
  align-items: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
`;

const SearchBox = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #F8FAFC;
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
  
  input {
    border: none; background: transparent; outline: none; width: 100%;
    color: #1E293B; font-size: 0.95rem;
  }
`;

const InviteButton = styled.button`
  background: #0F172A; color: white; border: none;
  padding: 10px 24px; border-radius: 10px;
  font-weight: 700; font-size: 0.9rem;
  display: flex; align-items: center; gap: 8px;
  cursor: pointer; transition: all 0.2s;
  
  &:hover { background: #1E293B; transform: translateY(-1px); }
`;

const UserTable = styled.table`
  width: 100%; border-collapse: separate; border-spacing: 0;
  background: white; border-radius: 20px; border: 1px solid #E2E8F0;
  overflow: hidden;

  th {
    background: #F8FAFC; padding: 18px; text-align: left;
    font-size: 0.75rem; font-weight: 800; color: #64748B;
    text-transform: uppercase; border-bottom: 1px solid #E2E8F0;
  }

  td {
    padding: 18px; border-bottom: 1px solid #F1F5F9;
    font-size: 0.9rem; color: #334155; vertical-align: middle;
  }

  tr:hover td { background: #FBFDFF; }
`;

const RoleBadge = styled.span`
  padding: 6px 12px; border-radius: 8px; font-size: 0.7rem; font-weight: 800;
  display: inline-flex; align-items: center; gap: 6px; text-transform: uppercase;
  
  ${props => props.$role === 'ADMIN' || props.$role === 'SUPER_ADMIN' ? `
    background: #F1F5F9; color: #0F172A; border: 1px solid #CBD5E1;
  ` : props.$role === 'SHERIFF' ? `
    background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE;
  ` : `
    background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0;
  `}
`;

const StatusToggle = styled.button`
  background: none; border: none; cursor: pointer;
  display: flex; align-items: center; gap: 6px;
  font-size: 0.75rem; font-weight: 700;
  color: ${props => props.$active ? '#16a34a' : '#dc2626'};
  opacity: 0.8; transition: opacity 0.2s;
  
  &:hover { opacity: 1; }
`;

// -----------------------------------------------------------------------------
// COMPONENT LOGIC
// -----------------------------------------------------------------------------

export default function UserList() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const res = await api.get('/users'); // Uses unified API
                setUsers(res.data || []);
            } catch (err) {
                console.error("User Registry Access Failed", err);
                toast.error("Unable to load personnel registry.");
            } finally {
                setLoading(false);
            }
        };
        fetchUsers();
    }, []);

    const toggleStatus = async (userId, currentStatus) => {
        const newStatus = currentStatus === 'active' ? 'suspended' : 'active';
        try {
            // Optimistic Update
            setUsers(prev => prev.map(u => u._id === userId ? { ...u, status: newStatus } : u));
            await api.patch(`/users/${userId}/status`, { status: newStatus });
            toast.success(`User ${newStatus === 'active' ? 'Activated' : 'Suspended'}`);
        } catch (err) {
            toast.error("Failed to update status.");
            // Revert on error
            setUsers(prev => prev.map(u => u._id === userId ? { ...u, status: currentStatus } : u));
        }
    };

    const filteredUsers = users.filter(u =>
        u.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.email?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <PageTransition>
            <PageContainer>
                <Header>
                    <div className="title-group">
                        <h1>Personnel Registry</h1>
                        <p>Access Control & Role Delegation</p>
                    </div>
                    <InviteButton onClick={() => toast.info("Invite Module Opening...")}>
                        <UserPlus size={18} /> Invite User
                    </InviteButton>
                </Header>

                <ControlBar>
                    <SearchBox>
                        <Search size={18} color="#94A3B8" />
                        <input
                            type="text"
                            placeholder="Search by Name, Email or Role..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </SearchBox>
                </ControlBar>

                <UserTable>
                    <thead>
                        <tr>
                            <th>Identity</th>
                            <th>Role & Access</th>
                            <th>Contact</th>
                            <th>Status</th>
                            <th>Last Active</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="6" style={{ textAlign: 'center', padding: '40px' }}>Loading Access Matrix...</td></tr>
                        ) : filteredUsers.map(user => (
                            <tr key={user._id}>
                                <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        <div style={{ width: '36px', height: '36px', background: '#F8FAFC', borderRadius: '50%', border: '1px solid #E2E8F0', display: 'grid', placeItems: 'center', fontWeight: '700', color: '#64748B' }}>
                                            {(user.name?.[0] || 'U').toUpperCase()}
                                        </div>
                                        <div style={{ fontWeight: '700', color: '#0F172A' }}>{user.name}</div>
                                    </div>
                                </td>
                                <td>
                                    <RoleBadge $role={user.role}>
                                        {user.role === 'ADMIN' ? <Shield size={12} /> :
                                            user.role === 'SHERIFF' ? <Briefcase size={12} /> : <Users size={12} />}
                                        {user.role}
                                    </RoleBadge>
                                </td>
                                <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: '#475569' }}>
                                        <Mail size={14} /> {user.email}
                                    </div>
                                </td>
                                <td>
                                    <StatusToggle
                                        $active={user.status === 'active'}
                                        onClick={() => toggleStatus(user._id, user.status)}
                                    >
                                        {user.status === 'active' ? <CheckCircle size={14} /> : <XCircle size={14} />}
                                        {user.status === 'active' ? 'ACTIVE' : 'LOCKED'}
                                    </StatusToggle>
                                </td>
                                <td style={{ color: '#94A3B8', fontSize: '0.8rem' }}>
                                    {user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Never'}
                                </td>
                                <td>
                                    <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94A3B8' }}>
                                        <MoreVertical size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </UserTable>
            </PageContainer>
        </PageTransition>
    );
}