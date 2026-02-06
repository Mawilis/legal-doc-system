/**
 * File: client/src/features/organization/pages/OrganizationSettings.jsx
 * STATUS: PRODUCTION-READY | EPITOME | TENANT COMMAND CENTER | BIBLICAL
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Tenant control panel for Law Firm Managers: profile, team, billing.
 * - Strictly scoped to the tenant of the signed-in user.
 *
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @platform, @security, @sre, @product, @design
 * - OPERATIONS: Ensure tenantService enforces tenant scoping server-side.
 * - SECURITY: Never expose tenant identifiers in client logs. Use secure cookies or auth tokens.
 * - TESTING: Unit tests should mock tenantService and auth store; add accessibility tests.
 * -----------------------------------------------------------------------------
 */

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import styled from 'styled-components';
import {
    Building, Users, CreditCard, Save, Plus, Activity, Shield
} from 'lucide-react';
import { toast } from 'react-toastify';
import debounce from 'lodash.debounce';
import PropTypes from 'prop-types';

// Services
import {
    getTenantSettings,
    updateTenantSettings,
    getTeamMembers,
    inviteTeamMember,
    updateUserStatus
} from '../services/tenantService';

// Auth store (assumed)
import useAuthStore from '../../../store/authStore';

// Small accessible modal (inline for single-file convenience)
function Modal({ title, open, onClose, children }) {
    useEffect(() => {
        function onKey(e) {
            if (e.key === 'Escape') onClose();
        }
        if (open) document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [open, onClose]);

    if (!open) return null;
    return (
        <ModalOverlay role="dialog" aria-modal="true" aria-label={title}>
            <ModalContent>
                <ModalHeader>
                    <h3>{title}</h3>
                    <CloseButton aria-label="Close" onClick={onClose}>✕</CloseButton>
                </ModalHeader>
                <ModalBody>{children}</ModalBody>
            </ModalContent>
        </ModalOverlay>
    );
}
Modal.propTypes = {
    title: PropTypes.string,
    open: PropTypes.bool,
    onClose: PropTypes.func,
    children: PropTypes.node
};

/* -------------------------
   Styled components
   ------------------------- */

const PageContainer = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  color: #0f172a;
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
`;

const Header = styled.div` margin-bottom: 2rem; `;
const Tabs = styled.div` display:flex; gap:2rem; border-bottom:1px solid #e2e8f0; margin-bottom:2rem; `;
const Tab = styled.button`
  background:none; border:none; padding:1rem 0; font-size:0.95rem; font-weight:600;
  color: ${p => p.$active ? '#2563EB' : '#64748B'};
  border-bottom: 2px solid ${p => p.$active ? '#2563EB' : 'transparent'};
  cursor:pointer; display:flex; align-items:center; gap:8px;
  &:focus { outline: 3px solid rgba(37,99,235,0.12); border-radius:4px; }
`;

const Card = styled.section`
  background:white; border-radius:12px; border:1px solid #E2E8F0; padding:2rem; margin-bottom:2rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
`;

const FormGroup = styled.div` margin-bottom:1.25rem; label{ display:block; font-weight:700; margin-bottom:0.5rem; } input, textarea { width:100%; padding:0.75rem; border-radius:8px; border:1px solid #CBD5E1; } `;
const Button = styled.button`
  display:inline-flex; align-items:center; gap:8px; padding:0.75rem 1.25rem; border-radius:8px; border:none; font-weight:700; cursor:pointer;
  ${p => p.$primary ? `background:#2563EB;color:#fff;` : `background:#F1F5F9;color:#334155;`}
  &:disabled { opacity:0.6; cursor:not-allowed; }
`;

const Table = styled.table` width:100%; border-collapse:collapse; th{ text-align:left; padding:1rem; background:#F8FAFC; color:#64748B; font-size:0.75rem; } td{ padding:1rem; border-bottom:1px solid #F1F5F9; } `;
const Badge = styled.span` padding:4px 8px; border-radius:999px; font-weight:700; font-size:0.75rem; ${p => p.$status === 'active' ? 'background:#DCFCE7;color:#166534;' : 'background:#FEE2E2;color:#991B1B;'} `;

/* Modal styles */
const ModalOverlay = styled.div` position:fixed; inset:0; background:rgba(2,6,23,0.6); display:flex; align-items:center; justify-content:center; z-index:1000; `;
const ModalContent = styled.div` background:white; border-radius:12px; width:520px; max-width:95%; padding:1rem; box-shadow:0 10px 30px rgba(2,6,23,0.2); `;
const ModalHeader = styled.div` display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; `;
const ModalBody = styled.div` padding-top:0.5rem; `;
const CloseButton = styled.button` background:none; border:none; font-size:1rem; cursor:pointer; `;

/* -------------------------
   Component
   ------------------------- */

export default function OrganizationSettings() {
    const { token, user } = useAuthStore(); // expects { token, user: { tenantId, role, _id } }
    const tenantId = user?.tenantId;

    const [activeTab, setActiveTab] = useState('general');
    const [loading, setLoading] = useState(true);

    // General settings
    const [firmName, setFirmName] = useState('');
    const [firmEmail, setFirmEmail] = useState('');
    const [primaryColor, setPrimaryColor] = useState('#10B981');
    const [saving, setSaving] = useState(false);

    // Team
    const [team, setTeam] = useState([]);
    const [teamLoading, setTeamLoading] = useState(false);

    // Invite modal
    const [inviteOpen, setInviteOpen] = useState(false);
    const [inviteEmail, setInviteEmail] = useState('');
    const [inviteFirstName, setInviteFirstName] = useState('');
    const [inviteLastName, setInviteLastName] = useState('');
    const [inviteRole, setInviteRole] = useState('LAWYER');
    const [inviteSubmitting, setInviteSubmitting] = useState(false);

    // Local helpers
    const isTenantAdmin = useMemo(() => String(user?.role).toUpperCase() === 'TENANT_ADMIN' || String(user?.role).toUpperCase() === 'SUPER_ADMIN', [user]);

    // Load data
    useEffect(() => {
        let mounted = true;
        async function load() {
            setLoading(true);
            try {
                const [settingsRes, teamRes] = await Promise.all([
                    getTenantSettings(token),
                    getTeamMembers(token)
                ]);
                if (!mounted) return;
                if (settingsRes?.data) {
                    setFirmName(settingsRes.data.name || '');
                    setFirmEmail(settingsRes.data.contact?.email || '');
                    setPrimaryColor(settingsRes.data.settings?.theme?.primaryColor || '#10B981');
                }
                if (teamRes?.data) setTeam(teamRes.data);
            } catch (err) {
                console.error('OrganizationSettings.load', err);
                toast.error('Failed to load organization data.');
            } finally {
                if (mounted) setLoading(false);
            }
        }
        if (tenantId) load();
        return () => { mounted = false; };
    }, [tenantId, token]);

    // Debounced save to avoid rapid calls
    const debouncedSave = useCallback(debounce(async (payload, onDone) => {
        try {
            await updateTenantSettings(token, payload);
            toast.success('Organization settings saved.');
            if (onDone) onDone(null);
        } catch (err) {
            console.error('OrganizationSettings.save', err);
            toast.error('Failed to save settings.');
            if (onDone) onDone(err);
        }
    }, 700), [token]);

    const handleSaveSettings = async () => {
        if (!isTenantAdmin) {
            toast.error('Insufficient permissions.');
            return;
        }
        // Basic validation
        if (!firmName || firmName.trim().length < 2) {
            toast.error('Please provide a valid firm name.');
            return;
        }
        if (firmEmail && !/^\S+@\S+\.\S+$/.test(firmEmail)) {
            toast.error('Please provide a valid email address.');
            return;
        }

        setSaving(true);
        debouncedSave({ name: firmName.trim(), contact: { email: firmEmail.trim() }, settings: { theme: { primaryColor } } }, (err) => {
            setSaving(false);
            if (!err) {
                // Optionally refresh team or settings
            }
        });
    };

    // Toggle user active status with optimistic UI
    const handleToggleStatus = async (userId, currentStatus) => {
        if (!isTenantAdmin) {
            toast.error('Insufficient permissions.');
            return;
        }
        // Optimistic update
        const prev = team;
        setTeam(prev.map(u => u._id === userId ? { ...u, isActive: !currentStatus } : u));
        try {
            await updateUserStatus(token, userId, !currentStatus);
            toast.info('User status updated.');
        } catch (err) {
            console.error('OrganizationSettings.toggleStatus', err);
            // rollback
            setTeam(prev);
            toast.error('Could not update user status.');
        }
    };

    // Invite flow
    const openInvite = () => {
        setInviteEmail('');
        setInviteFirstName('');
        setInviteLastName('');
        setInviteRole('LAWYER');
        setInviteOpen(true);
    };

    const submitInvite = async () => {
        if (!inviteEmail || !/^\S+@\S+\.\S+$/.test(inviteEmail)) {
            toast.error('Please enter a valid email.');
            return;
        }
        setInviteSubmitting(true);
        try {
            const res = await inviteTeamMember(token, { email: inviteEmail, role: inviteRole, firstName: inviteFirstName, lastName: inviteLastName });
            // Optionally refresh team list
            try {
                const teamRes = await getTeamMembers(token);
                if (teamRes?.data) setTeam(teamRes.data);
            } catch (_) { /* ignore */ }

            toast.success(res?.message || 'Invitation created.');
            setInviteOpen(false);
        } catch (err) {
            console.error('OrganizationSettings.invite', err);
            toast.error(err?.message || 'Failed to create invite.');
        } finally {
            setInviteSubmitting(false);
        }
    };

    if (loading) return <PageContainer>Loading Organization Console...</PageContainer>;

    return (
        <PageContainer>
            <Header>
                <h1 style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <Building size={32} /> Organization Settings
                </h1>
                <p style={{ color: '#64748B', marginTop: 6 }}>Manage your Law Firm's profile, team members, and billing.</p>
            </Header>

            <Tabs role="tablist" aria-label="Organization sections">
                <Tab role="tab" aria-selected={activeTab === 'general'} $active={activeTab === 'general'} onClick={() => setActiveTab('general')}>
                    <Shield size={18} /> General & Branding
                </Tab>
                <Tab role="tab" aria-selected={activeTab === 'team'} $active={activeTab === 'team'} onClick={() => setActiveTab('team')}>
                    <Users size={18} /> Team Management
                </Tab>
                <Tab role="tab" aria-selected={activeTab === 'billing'} $active={activeTab === 'billing'} onClick={() => setActiveTab('billing')}>
                    <CreditCard size={18} /> Billing & Plan
                </Tab>
            </Tabs>

            {/* GENERAL */}
            {activeTab === 'general' && (
                <Card aria-labelledby="general-heading">
                    <h3 id="general-heading" style={{ marginBottom: 16 }}>Firm Profile</h3>

                    <FormGroup>
                        <label htmlFor="firmName">Registered Firm Name</label>
                        <input id="firmName" value={firmName} onChange={e => setFirmName(e.target.value)} aria-required="true" />
                    </FormGroup>

                    <FormGroup>
                        <label htmlFor="firmEmail">Administrative Contact Email</label>
                        <input id="firmEmail" type="email" value={firmEmail} onChange={e => setFirmEmail(e.target.value)} />
                    </FormGroup>

                    <FormGroup>
                        <label>Brand Primary Color (White Label)</label>
                        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                            <input aria-label="Primary color" type="color" value={primaryColor} onChange={e => setPrimaryColor(e.target.value)} style={{ width: 56, height: 40, borderRadius: 8, border: '1px solid #CBD5E1' }} />
                            <input value={primaryColor} onChange={e => setPrimaryColor(e.target.value)} aria-label="Primary color hex" />
                        </div>
                    </FormGroup>

                    <div style={{ display: 'flex', gap: 12 }}>
                        <Button $primary onClick={handleSaveSettings} disabled={saving}>{saving ? 'Saving...' : <><Save size={16} /> Save Changes</>}</Button>
                        <Button onClick={() => { setFirmName(''); setFirmEmail(''); setPrimaryColor('#10B981'); }}>Reset</Button>
                    </div>
                </Card>
            )}

            {/* TEAM */}
            {activeTab === 'team' && (
                <Card aria-labelledby="team-heading">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <h3 id="team-heading" style={{ margin: 0 }}>Team Roster ({team.length})</h3>
                        <div style={{ display: 'flex', gap: 8 }}>
                            <Button onClick={openInvite}><Plus size={16} /> Invite</Button>
                        </div>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                        <Table role="table" aria-label="Team members">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {team.map(user => (
                                    <tr key={user._id}>
                                        <td><strong>{user.firstName} {user.lastName}</strong></td>
                                        <td>{user.email}</td>
                                        <td>{user.role}</td>
                                        <td><Badge $status={user.isActive ? 'active' : 'inactive'}>{user.isActive ? 'ACTIVE' : 'SUSPENDED'}</Badge></td>
                                        <td>
                                            <Button onClick={() => handleToggleStatus(user._id, user.isActive)} aria-label={`Toggle status for ${user.email}`}>
                                                {user.isActive ? 'Suspend' : 'Activate'}
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    </div>
                </Card>
            )}

            {/* BILLING */}
            {activeTab === 'billing' && (
                <Card style={{ textAlign: 'center', padding: '3rem' }}>
                    <Activity size={48} color="#CBD5E1" style={{ marginBottom: '1rem' }} />
                    <h3>Billing Engine Connect</h3>
                    <p style={{ color: '#64748B' }}>To be integrated with Stripe/PayGate in the next sprint.</p>
                </Card>
            )}

            {/* Invite Modal */}
            <Modal title="Invite Team Member" open={inviteOpen} onClose={() => setInviteOpen(false)}>
                <FormGroup>
                    <label htmlFor="inviteEmail">Email</label>
                    <input id="inviteEmail" type="email" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} />
                </FormGroup>
                <FormGroup>
                    <label htmlFor="inviteFirst">First Name</label>
                    <input id="inviteFirst" value={inviteFirstName} onChange={e => setInviteFirstName(e.target.value)} />
                </FormGroup>
                <FormGroup>
                    <label htmlFor="inviteLast">Last Name</label>
                    <input id="inviteLast" value={inviteLastName} onChange={e => setInviteLastName(e.target.value)} />
                </FormGroup>
                <FormGroup>
                    <label htmlFor="inviteRole">Role</label>
                    <select id="inviteRole" value={inviteRole} onChange={e => setInviteRole(e.target.value)}>
                        <option value="LAWYER">Lawyer</option>
                        <option value="PARALEGAL">Paralegal</option>
                        <option value="TENANT_ADMIN">Admin</option>
                    </select>
                </FormGroup>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                    <Button onClick={() => setInviteOpen(false)}>Cancel</Button>
                    <Button $primary onClick={submitInvite} disabled={inviteSubmitting}>{inviteSubmitting ? 'Sending...' : 'Send Invite'}</Button>
                </div>
            </Modal>
        </PageContainer>
    );
}
