// ~/legal-doc-system/client/src/features/admin/pages/AdminPanel.jsx

import React, { useEffect, useState, useCallback } from 'react';
import styled from 'styled-components';
import io from 'socket.io-client';
import {
    getAllUsers,
    createUser,
} from '../services/adminService';
import { FaPlus, FaChartBar, FaUsers, FaCog, FaListAlt, FaDownload } from 'react-icons/fa';
import { toast } from 'react-toastify';
import Button from '../../components/StyledButton';
import {
    LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'; // ✅ Import chart components

// --- Constants ---
const SERVER_URL = process.env.REACT_APP_SERVER_URL || 'http://localhost:5000';

// --- API Service Function (should be in adminService.js) ---
const getAuditLogs = async () => {
    const response = await fetch(`${SERVER_URL}/api/audit`);
    if (!response.ok) {
        throw new Error('Failed to fetch audit logs');
    }
    return response.json();
};

// --- Mock Data for Analytics Chart ---
const loginData = [
    { name: 'Mon', logins: 120 },
    { name: 'Tue', logins: 210 },
    { name: 'Wed', logins: 170 },
    { name: 'Thu', logins: 250 },
    { name: 'Fri', logins: 310 },
    { name: 'Sat', logins: 180 },
    { name: 'Sun', logins: 220 },
];


/**
 * A production-ready AdminPanel component for managing users, teams, logs, and settings.
 * Features a real-time, drag-and-drop interface for team management and an audit log viewer.
 */
const AdminPanel = () => {
    // --- State Management ---
    const [users, setUsers] = useState({});
    const [teams, setTeams] = useState({});
    const [loading, setLoading] = useState(true);
    const [modalOpen, setModalOpen] = useState(false);
    const [newUser, setNewUser] = useState({ name: '', email: '', password: '', role: 'user' });
    const [auditLogs, setAuditLogs] = useState([]);
    const [auditLoading, setAuditLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('users');
    const [draggedItem, setDraggedItem] = useState(null);

    // --- Data Fetching Callbacks ---
    const fetchUsersAndTeams = useCallback(async () => {
        setLoading(true);
        try {
            const usersData = await getAllUsers();
            const userMap = usersData.reduce((acc, user) => {
                acc[user._id] = user;
                return acc;
            }, {});
            setUsers(userMap);

            const initialTeams = { 'Team Alpha': [], 'Team Beta': [], 'Unassigned': [] };
            usersData.forEach((user, index) => {
                if (index < 2) initialTeams['Team Alpha'].push(user._id);
                else if (index < 4) initialTeams['Team Beta'].push(user._id);
                else initialTeams['Unassigned'].push(user._id);
            });
            setTeams(initialTeams);
        } catch (error) {
            toast.error('Failed to load user data.');
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchAuditLogs = useCallback(async () => {
        setAuditLoading(true);
        try {
            const response = await getAuditLogs();
            setAuditLogs(response.data);
        } catch (error) {
            toast.error(error.message || 'Could not fetch audit logs.');
        } finally {
            setAuditLoading(false);
        }
    }, []);

    // --- Effects ---
    useEffect(() => {
        if (activeTab === 'users') {
            fetchUsersAndTeams();
        } else if (activeTab === 'logs') {
            fetchAuditLogs();
        }
    }, [activeTab, fetchUsersAndTeams, fetchAuditLogs]);

    useEffect(() => {
        const socket = io(SERVER_URL);
        const handleTeamsUpdate = (updatedTeams) => {
            setTeams(updatedTeams);
            toast.success(`Team assignments were updated in real-time.`);
        };
        socket.on('teams_updated', handleTeamsUpdate);
        return () => {
            socket.off('teams_updated', handleTeamsUpdate);
            socket.disconnect();
        };
    }, []);

    // --- Event Handlers ---
    const handleDragStart = (e, userId, sourceTeam) => {
        setDraggedItem({ userId, sourceTeam });
        e.dataTransfer.effectAllowed = 'move';
        setTimeout(() => { e.target.style.opacity = '0.5'; }, 0);
    };
    const handleDragEnd = (e) => { e.target.style.opacity = '1'; setDraggedItem(null); };
    const handleDragOver = (e) => { e.preventDefault(); };
    const handleDrop = (e, destinationTeam) => {
        e.preventDefault();
        if (!draggedItem || draggedItem.sourceTeam === destinationTeam) return;

        const newTeams = { ...teams };
        newTeams[draggedItem.sourceTeam] = newTeams[draggedItem.sourceTeam].filter(id => id !== draggedItem.userId);
        newTeams[destinationTeam] = [...newTeams[destinationTeam], draggedItem.userId];
        setTeams(newTeams);
        toast.success(`User moved to ${destinationTeam}.`);
    };

    const handleCreateUser = async (e) => {
        e.preventDefault();
        try {
            const newUserResponse = await createUser(newUser);
            toast.success('User created successfully.');
            setModalOpen(false);
            setNewUser({ name: '', email: '', password: '', role: 'user' });
            setUsers(prev => ({ ...prev, [newUserResponse._id]: newUserResponse }));
            setTeams(prev => ({ ...prev, 'Unassigned': [...prev['Unassigned'], newUserResponse._id] }));
        } catch (error) {
            toast.error(error.response?.data?.message || 'Failed to create user.');
        }
    };

    return (
        <Container>
            <TabBar>
                <TabButton active={activeTab === 'users'} onClick={() => setActiveTab('users')}><FaUsers /> Team Management</TabButton>
                <TabButton active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')}><FaChartBar /> Analytics</TabButton>
                <TabButton active={activeTab === 'logs'} onClick={() => setActiveTab('logs')}><FaListAlt /> Audit Logs</TabButton>
                <TabButton active={activeTab === 'settings'} onClick={() => setActiveTab('settings')}><FaCog /> Settings</TabButton>
            </TabBar>

            {activeTab === 'users' && (
                <>
                    <Header>
                        <h2>Team Assignments</h2>
                        <Button variant="success" onClick={() => setModalOpen(true)}><FaPlus /> Add User</Button>
                    </Header>
                    <TeamsContainer>
                        {loading ? <p>Loading teams...</p> : Object.entries(teams).map(([teamName, userIds]) => (
                            <TeamColumn key={teamName} onDragOver={handleDragOver} onDrop={(e) => handleDrop(e, teamName)}>
                                <h3>{teamName} ({userIds.length})</h3>
                                <UserList>
                                    {userIds.map(userId => users[userId] && (
                                        <UserCard key={userId} draggable onDragStart={(e) => handleDragStart(e, userId, teamName)} onDragEnd={handleDragEnd}>
                                            {users[userId].name}
                                            <small>{users[userId].email}</small>
                                        </UserCard>
                                    ))}
                                </UserList>
                            </TeamColumn>
                        ))}
                    </TeamsContainer>
                </>
            )}

            {activeTab === 'analytics' && (
                <AnalyticsContainer>
                    <Header><h2>Analytics Dashboard</h2></Header>
                    <ChartBox>
                        <h4>Weekly User Logins</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={loginData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey="logins" stroke="#007bff" strokeWidth={2} />
                            </LineChart>
                        </ResponsiveContainer>
                    </ChartBox>
                </AnalyticsContainer>
            )}

            {activeTab === 'logs' && (
                <Panel>
                    <Header>
                        <h2>Audit Logs</h2>
                        <Button variant="secondary" onClick={() => window.open(`${SERVER_URL}/api/audit/export/csv`, '_blank')}>
                            <FaDownload /> Export CSV
                        </Button>
                    </Header>
                    {auditLoading ? <p>Loading audit logs...</p> : (
                        <AuditTable>
                            <thead>
                                <tr>
                                    <th>User</th><th>Action</th><th>Status</th><th>Time</th><th>IP Address</th>
                                </tr>
                            </thead>
                            <tbody>
                                {auditLogs.length > 0 ? auditLogs.map(log => (
                                    <tr key={log._id}>
                                        <td>{log.user?.name || log.email}</td>
                                        <td><MethodTag method={log.method}>{log.method}</MethodTag> {log.path}</td>
                                        <td><StatusTag status={log.status}>{log.status}</StatusTag></td>
                                        <td>{new Date(log.createdAt).toLocaleString()}</td>
                                        <td>{log.ip}</td>
                                    </tr>
                                )) : (
                                    <tr><td colSpan="5" style={{ textAlign: 'center' }}>No audit logs found.</td></tr>
                                )}
                            </tbody>
                        </AuditTable>
                    )}
                </Panel>
            )}

            {activeTab === 'settings' && (<SettingsPanel>Application Settings</SettingsPanel>)}

            {modalOpen && (
                <ModalOverlay>
                    <ModalContent onSubmit={handleCreateUser}>
                        <h3>Create New User</h3>
                        <input type="text" placeholder="Name" required value={newUser.name} onChange={(e) => setNewUser({ ...newUser, name: e.target.value })} />
                        <input type="email" placeholder="Email" required value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} />
                        <input type="password" placeholder="Password" required value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} />
                        <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>
                            <option value="user">User</option>
                            <option value="admin">Admin</option>
                        </select>
                        <ModalActions>
                            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
                            <Button type="submit" variant="success">Create</Button>
                        </ModalActions>
                    </ModalContent>
                </ModalOverlay>
            )}
        </Container>
    );
};

export default AdminPanel;

// --- Styled Components ---

const Container = styled.div` padding: 2rem; background-color: #f4f6f8; min-height: 100vh; `;
const Header = styled.div` font-size: 1.75rem; color: #333; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; h2 { margin: 0; font-size: 1.75rem; }`;
const TabBar = styled.div` display: flex; gap: 0.5rem; margin-bottom: 1.5rem; border-bottom: 2px solid #dee2e6; `;
const TabButton = styled.button`
  display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem;
  border: none; background-color: transparent;
  color: ${({ active }) => (active ? '#007bff' : '#555')};
  border-bottom: 3px solid ${({ active }) => (active ? '#007bff' : 'transparent')};
  cursor: pointer; font-size: 1rem; font-weight: 500;
  transition: all 0.2s ease-in-out;
  &:hover { color: #0056b3; background-color: #e9ecef; }
`;
const TeamsContainer = styled.div` display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; `;
const TeamColumn = styled.div`
    background-color: #fff; border-radius: 8px; padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border: 2px dashed transparent;
    h3 { margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 0.75rem; color: #495057; }
`;
const UserList = styled.div` min-height: 200px; display: flex; flex-direction: column; gap: 0.75rem; `;
const UserCard = styled.div`
    background-color: #f8f9fa; padding: 0.75rem 1rem; border-radius: 5px;
    border: 1px solid #dee2e6; cursor: grab;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    display: flex; flex-direction: column;
    &:active { cursor: grabbing; }
    &:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.1); transform: translateY(-2px); }
    small { color: #6c757d; font-size: 0.8rem; margin-top: 0.25rem; }
`;
const ModalOverlay = styled.div` position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; `;
const ModalContent = styled.form`
  background: white; padding: 2rem; border-radius: 8px;
  width: 100%; max-width: 400px; display: flex; flex-direction: column; gap: 1rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  h3 { margin-top: 0; text-align: center; }
  input, select { padding: 0.75rem; font-size: 1rem; width: 100%; border-radius: 4px; border: 1px solid #ccc; }
`;
const ModalActions = styled.div` display: flex; justify-content: flex-end; gap: 10px; margin-top: 1rem; `;
const Panel = styled.div` background: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); `;
const SettingsPanel = styled(Panel)``;
const AnalyticsContainer = styled(Panel)``;
const ChartBox = styled.div`
    background: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    h4 { text-align: center; margin-top: 0; margin-bottom: 1rem; color: #495057; }
`;
const AuditTable = styled.table`
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    th, td { padding: 0.75rem 1rem; border-bottom: 1px solid #ddd; text-align: left; vertical-align: middle; }
    th { background-color: #f8f9fa; font-weight: 600; }
    tr:hover { background-color: #f1f1f1; }
`;
const StatusTag = styled.span`
    padding: 0.2rem 0.5rem;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #fff;
    background-color: ${({ status }) => status === 'SUCCESS' ? '#28a745' : '#dc3545'};
`;
const MethodTag = styled.span`
    font-family: 'Courier New', Courier, monospace;
    font-weight: bold;
    color: #007bff;
`;
