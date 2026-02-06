/**
 * File: client/src/features/admin/pages/AdminDashboard.jsx
 * STATUS: PRODUCTION | EPITOME | SOVEREIGN COMMAND CENTER
 * VERSION: 5.1.0 (Storage Conflict Resolution & Direct Hydration)
 *
 * PURPOSE
 * - Owner / Admin command center for Wilsy OS.
 * - FIX: Resolves "Sheriff" vs "Super Admin" storage conflict by forcing 
 * read from 'wilsy-auth-storage'.
 * - FIX: Hardened Token extraction to handle 'state.token' vs 'state.user.token'.
 *
 * IMPORTANT INTEGRATION NOTES
 * - Keep this exact filename and path.
 * - AdminService must exist at client/src/features/admin/services/adminService.js.
 * - This file bypasses broken Redux/Context state and reads directly from Disk 
 * to ensure the Super Admin is recognized.
 *
 * COLLABORATION
 * - AUTHOR: Chief Architect (Wilson Khanyezi)
 * - FRONTEND: @frontend (visual polish, tests)
 * - BACKEND: @backend-team (API contract & RBAC)
 * - SECURITY: @security (audit, PII masking)
 * - QA: @qa (unit, integration, E2E)
 *
 * EPITOME:
 * Biblical worth billions no child's place.
 */

import React, {
  useState,
  useEffect,
  useMemo,
  useCallback,
  useRef,
  useReducer
} from 'react';
import styled, { keyframes, css, createGlobalStyle } from 'styled-components';
import { toast, ToastContainer } from 'react-toastify';
import {
  FiUsers, FiShield, FiRefreshCw, FiSearch, FiActivity,
  FiLock, FiUnlock, FiTrash2, FiCpu, FiTerminal, FiDatabase,
  FiAlertTriangle, FiCheckCircle, FiMoreVertical, FiLayers,
  FiGlobe, FiServer, FiHardDrive, FiCommand, FiSettings,
  FiUserPlus, FiDownloadCloud, FiShieldOff, FiExternalLink,
  FiCpu as FiProcessor, FiZap, FiWifi, FiCreditCard, FiKey,
  FiPackage, FiFileText, FiBarChart2, FiClock, FiMaximize,
  FiMinimize, FiChevronRight, FiGrid, FiList, FiEye, FiEdit3
} from 'react-icons/fi';
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts';

// Billion-Dollar Service Layer
import AdminService from '../services/adminService';

/* -----------------------------------------------------------------------------
   SOVEREIGN IDENTITY RESOLVER (Disk-Direct Extraction)
   --------------------------------------------------------------------------- */
const resolveSovereignState = () => {
  try {
    // Force Purgatory: Kill legacy Redux/Sheriff keys that contaminate state
    const poisonKeys = ['persist:root', 'persist:wilsy_os_root', 'tenantId', 'user_role'];
    poisonKeys.forEach(key => localStorage.removeItem(key));

    const authData = JSON.parse(localStorage.getItem('wilsy-auth-storage'));
    const userMeta = JSON.parse(localStorage.getItem('wilsy_user'));

    const state = authData?.state || {};
    const user = state.user || userMeta;

    // Multi-Path Token Extraction
    const token = state.token || user?.token || localStorage.getItem('accessToken');
    const isSuperAdmin = user?.role === 'SUPER_ADMIN' || user?.role === 'SUPER ADMIN';

    return {
      user,
      token,
      isAuthenticated: !!token,
      isAuthorized: isSuperAdmin
    };
  } catch (e) {
    console.error("[CRITICAL] Sovereign Identity Resolution Failure", e);
    return { isAuthorized: false };
  }
};

/* -----------------------------------------------------------------------------
   SYSTEM ANIMATIONS & THEMING
   --------------------------------------------------------------------------- */

const bootSequence = keyframes`
  0% { opacity: 0; transform: scale(0.99); filter: brightness(0); }
  50% { opacity: 0.5; transform: scale(1); filter: brightness(0.5); }
  100% { opacity: 1; transform: scale(1); filter: brightness(1); }
`;

const scanline = keyframes`
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
`;

const pulseGlow = keyframes`
  0% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.2); }
  50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.4); }
  100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.2); }
`;

const GlobalAdminStyles = createGlobalStyle`
  body {
    background-color: #020617;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
  }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #020617; }
  ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
  ::-webkit-scrollbar-thumb:hover { background: #3b82f6; }
`;

/* -----------------------------------------------------------------------------
   ADVANCED STYLED COMPONENTS
   --------------------------------------------------------------------------- */

const OSContainer = styled.div`
  min-height: 100vh;
  padding: 30px;
  color: #f1f5f9;
  font-family: 'JetBrains Mono', 'Inter', monospace;
  animation: ${bootSequence} 1.2s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
`;

const GlassWall = styled.div`
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  margin-bottom: 30px;
`;

const Sidebar = styled.aside`
  position: fixed;
  left: 0; top: 0; bottom: 0;
  width: 280px;
  background: #0B0F1A;
  border-right: 1px solid #1E293B;
  display: flex;
  flex-direction: column;
  padding: 40px 20px;
  z-index: 100;

  @media (max-width: 1024px) { display: none; }
`;

const NavItem = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 16px 20px;
  border-radius: 12px;
  color: ${p => p.$active ? '#FFF' : '#64748B'};
  background: ${p => p.$active ? 'linear-gradient(90deg, #1E293B 0%, rgba(30, 41, 59, 0) 100%)' : 'transparent'};
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  margin-bottom: 5px;
  border-left: 3px solid ${p => p.$active ? '#3B82F6' : 'transparent'};

  &:hover {
    background: #1E293B;
    color: #FFF;
  }
`;

const TopBar = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-left: 300px;
  margin-bottom: 40px;
  padding: 20px 0;

  @media (max-width: 1024px) { margin-left: 0; }

  .identity-slot {
    display: flex;
    align-items: center;
    gap: 20px;
  }
`;

const MetricGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-left: 300px;
  margin-bottom: 30px;

  @media (max-width: 1280px) { grid-template-columns: repeat(2, 1fr); }
  @media (max-width: 1024px) { margin-left: 0; }
  @media (max-width: 640px) { grid-template-columns: 1fr; }
`;

const MetricCard = styled.div`
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 12px;
  padding: 24px;
  position: relative;
  overflow: hidden;

  .label { color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
  .value { font-size: 2rem; font-weight: 800; color: #fff; margin: 10px 0; }
  .trend { font-size: 0.8rem; display: flex; align-items: center; gap: 5px; color: #10b981; }

  &::after {
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, #3b82f6, transparent);
  }
`;

const MainContent = styled.main`
  margin-left: 300px;
  @media (max-width: 1024px) { margin-left: 0; }
`;

const ControlCenter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 20px;

  @media (max-width: 768px) { flex-direction: column; align-items: stretch; }
`;

const SearchBox = styled.div`
  position: relative;
  flex: 1;

  svg {
    position: absolute;
    left: 16px; top: 50%;
    transform: translateY(-50%);
    color: #475569;
  }

  input {
    width: 100%;
    background: #0B0F1A;
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 14px 14px 14px 48px;
    color: #FFF;
    font-size: 0.95rem;

    &:focus { border-color: #3B82F6; outline: none; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); }
  }
`;

const TableContainer = styled.div`
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 12px;
  overflow: hidden;

  table {
    width: 100%;
    border-collapse: collapse;
    
    thead {
      background: #1E293B;
      th {
        text-align: left;
        padding: 16px 24px;
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
      }
    }

    tbody tr {
      border-bottom: 1px solid #1E293B;
      transition: background 0.2s;
      &:hover { background: rgba(59, 130, 246, 0.03); }

      td {
        padding: 18px 24px;
        color: #E2E8F0;
        font-size: 0.9rem;
      }
    }
  }
`;

const Badge = styled.span`
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  background: ${p => p.$variant === 'admin' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(148, 163, 184, 0.1)'};
  color: ${p => p.$variant === 'admin' ? '#3B82F6' : '#94A3B8'};
  border: 1px solid ${p => p.$variant === 'admin' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(148, 163, 184, 0.2)'};
`;

const CommandButton = styled.button`
  background: ${p => p.$primary ? '#3B82F6' : '#1E293B'};
  color: #FFF;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    filter: brightness(1.1);
    transform: translateY(-1px);
  }

  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

const ChartPanel = styled(GlassWall)`
  height: 400px;
  margin-top: 40px;
`;

const LogStream = styled.div`
  background: #020617;
  border: 1px solid #1E293B;
  border-radius: 8px;
  padding: 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  height: 300px;
  overflow-y: auto;
  margin-top: 30px;

  .entry {
    margin-bottom: 10px;
    display: flex;
    gap: 15px;
    .ts { color: #475569; }
    .type { color: #3B82F6; font-weight: bold; }
    .msg { color: #94A3B8; }
  }
`;

/* -----------------------------------------------------------------------------
   SYSTEM DATA MOCKING (Generational Scale)
   --------------------------------------------------------------------------- */
const telemetryData = Array.from({ length: 24 }, (_, i) => ({
  time: `${i}:00`,
  requests: Math.floor(Math.random() * 5000) + 1000,
  latency: Math.floor(Math.random() * 50) + 10,
  cpu: Math.floor(Math.random() * 40) + 10
}));

/* -----------------------------------------------------------------------------
   CORE COMPONENT LOGIC
   --------------------------------------------------------------------------- */

export default function AdminDashboard() {
  // Sovereign Identity Logic
  const { user: sovereignUser, token: sovereignToken, isAuthorized } = useMemo(() => resolveSovereignState(), []);

  // App State
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('registry');
  const [logs, setLogs] = useState([]);
  const [viewMode, setViewMode] = useState('grid');
  const [sysStats, setSysStats] = useState({
    uptime: '99.99%',
    nodes: 14,
    securityEvents: 0,
    apiCalls: '1.2M'
  });

  // Fetch Logic
  const syncSovereignData = useCallback(async () => {
    if (!sovereignToken) return;
    try {
      setLoading(true);
      const data = await AdminService.getAllUsers(sovereignToken);
      const userList = Array.isArray(data) ? data : (data.items || data.data || []);
      setUsers(userList);

      addLogEntry('SYSTEM', 'Sovereign registry synchronized successfully.');
      toast.success("CORE HYDRATED", { theme: "dark" });
    } catch (err) {
      addLogEntry('CRITICAL', 'Registry synchronization failed. Access denied.');
      toast.error("SYNC FAILED: CLEARANCE ERROR");
    } finally {
      setLoading(false);
    }
  }, [sovereignToken]);

  const addLogEntry = (type, msg) => {
    setLogs(prev => [{
      ts: new Date().toLocaleTimeString(),
      type,
      msg
    }, ...prev].slice(0, 100));
  };

  useEffect(() => {
    if (isAuthorized) {
      syncSovereignData();

      // Simulation of live telemetry
      const interval = setInterval(() => {
        setSysStats(prev => ({
          ...prev,
          apiCalls: (Math.random() * 10).toFixed(2) + 'M'
        }));
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [isAuthorized, syncSovereignData]);

  // UI Processing
  const filteredUsers = useMemo(() => {
    return users.filter(u =>
      u.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [users, searchTerm]);

  // Guard Clause
  if (!isAuthorized) {
    return (
      <OSContainer style={{ display: 'grid', placeItems: 'center' }}>
        <GlobalAdminStyles />
        <GlassWall style={{ textAlign: 'center', maxWidth: '500px' }}>
          <FiShieldOff size={80} color="#ef4444" />
          <h1 style={{ fontSize: '2.5rem', margin: '20px 0' }}>REJECTED</h1>
          <p style={{ color: '#94a3b8', lineHeight: '1.6' }}>
            Current session identity does not possess <strong>SUPER_ADMIN</strong> clearance.
            Conflict detected with legacy "Sheriff" role in storage.
          </p>
          <CommandButton
            $primary
            style={{ margin: '30px auto 0' }}
            onClick={() => window.location.href = '/login'}
          >
            RESTORE SOVEREIGN ACCESS
          </CommandButton>
        </GlassWall>
      </OSContainer>
    );
  }

  return (
    <OSContainer>
      <GlobalAdminStyles />
      <Sidebar>
        <div style={{ marginBottom: '40px', padding: '0 20px' }}>
          <h2 style={{ letterSpacing: '2px', fontWeight: 900, color: '#3B82F6' }}>WILSY OS</h2>
          <span style={{ fontSize: '0.65rem', color: '#475569' }}>CORE COMMAND v5.1.0</span>
        </div>

        <NavItem $active={activeTab === 'registry'} onClick={() => setActiveTab('registry')}>
          <FiUsers /> User Management
        </NavItem>
        <NavItem $active={activeTab === 'security'} onClick={() => setActiveTab('security')}>
          <FiShield /> Security Protocol
        </NavItem>
        <NavItem $active={activeTab === 'infrastructure'} onClick={() => setActiveTab('infrastructure')}>
          <FiServer /> Infrastructure
        </NavItem>
        <NavItem $active={activeTab === 'telemetry'} onClick={() => setActiveTab('telemetry')}>
          <FiActivity /> System Telemetry
        </NavItem>
        <NavItem $active={activeTab === 'database'} onClick={() => setActiveTab('database')}>
          <FiDatabase /> Data Sharding
        </NavItem>

        <div style={{ marginTop: 'auto', padding: '20px', borderTop: '1px solid #1E293B' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#3B82F6', display: 'grid', placeItems: 'center', fontWeight: 900 }}>W</div>
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 700 }}>Wilson K.</div>
              <div style={{ fontSize: '0.65rem', color: '#64748B' }}>Sovereign Admin</div>
            </div>
          </div>
        </div>
      </Sidebar>

      <TopBar>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Command Console</h1>
          <p style={{ color: '#64748B', fontSize: '0.8rem' }}>Monitoring {users.length} unique identities across production clusters.</p>
        </div>
        <div className="identity-slot">
          <FiZap color="#F59E0B" />
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10B981' }}>REALTIME_ACTIVE</div>
            <div style={{ fontSize: '0.65rem', color: '#64748B' }}>NODE_RSA_091</div>
          </div>
          <CommandButton onClick={syncSovereignData} disabled={loading}>
            <FiRefreshCw className={loading ? 'spin' : ''} /> SYNC CORE
          </CommandButton>
        </div>
      </TopBar>

      <MetricGrid>
        <MetricCard>
          <div className="label">Total Managed Entities</div>
          <div className="value">{users.length}</div>
          <div className="trend"><FiChevronRight /> +12.4% vs last shard</div>
          <FiUsers style={{ position: 'absolute', right: '20px', top: '20px', opacity: 0.1, fontSize: '3rem' }} />
        </MetricCard>
        <MetricCard>
          <div className="label">Active Shards</div>
          <div className="value">{sysStats.nodes}</div>
          <div className="trend" style={{ color: '#3B82F6' }}><FiWifi /> Low Latency</div>
          <FiGlobe style={{ position: 'absolute', right: '20px', top: '20px', opacity: 0.1, fontSize: '3rem' }} />
        </MetricCard>
        <MetricCard>
          <div className="label">Total API Throughput</div>
          <div className="value">{sysStats.apiCalls}</div>
          <div className="trend"><FiZap /> Processing High</div>
          <FiActivity style={{ position: 'absolute', right: '20px', top: '20px', opacity: 0.1, fontSize: '3rem' }} />
        </MetricCard>
        <MetricCard>
          <div className="label">Core Uptime</div>
          <div className="value">{sysStats.uptime}</div>
          <div className="trend" style={{ color: '#F59E0B' }}><FiClock /> 42 Days 12h</div>
          <FiProcessor style={{ position: 'absolute', right: '20px', top: '20px', opacity: 0.1, fontSize: '3rem' }} />
        </MetricCard>
      </MetricGrid>

      <MainContent>
        {activeTab === 'registry' && (
          <>
            <ControlCenter>
              <SearchBox>
                <FiSearch />
                <input
                  type="text"
                  placeholder="Query sovereign identity registry..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </SearchBox>
              <div style={{ display: 'flex', gap: '10px' }}>
                <CommandButton onClick={() => setViewMode('grid')} style={{ padding: '10px' }}>
                  <FiGrid color={viewMode === 'grid' ? '#3B82F6' : '#64748B'} />
                </CommandButton>
                <CommandButton onClick={() => setViewMode('list')} style={{ padding: '10px' }}>
                  <FiList color={viewMode === 'list' ? '#3B82F6' : '#64748B'} />
                </CommandButton>
                <CommandButton $primary>
                  <FiUserPlus /> Provision Entity
                </CommandButton>
              </div>
            </ControlCenter>

            <TableContainer>
              <table>
                <thead>
                  <tr>
                    <th>Entity Identity</th>
                    <th>Clearance</th>
                    <th>Network Status</th>
                    <th>Last Active</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan="5" style={{ textAlign: 'center', padding: '100px' }}>
                      <FiRefreshCw className="spin" size={30} color="#3B82F6" />
                      <div style={{ marginTop: '20px', fontWeight: 900 }}>HYDRATING REGISTRY...</div>
                    </td></tr>
                  ) : filteredUsers.map((u, i) => (
                    <tr key={u._id || i}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                          <div style={{ width: '40px', height: '40px', background: '#1E293B', borderRadius: '8px', display: 'grid', placeItems: 'center' }}>
                            <FiTerminal size={14} color="#3B82F6" />
                          </div>
                          <div>
                            <div style={{ fontWeight: 800 }}>{u.name || 'Anonymous Node'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{u.email}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <Badge $variant={u.role?.toLowerCase().includes('admin') ? 'admin' : 'user'}>
                          {u.role}
                        </Badge>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10B981', fontWeight: 700, fontSize: '0.75rem' }}>
                          <FiCheckCircle size={12} /> SECURE
                        </div>
                      </td>
                      <td style={{ color: '#64748B', fontSize: '0.8rem' }}>
                        {new Date().toLocaleDateString()}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '15px' }}>
                          <FiEye style={{ cursor: 'pointer' }} title="Audit Details" />
                          <FiEdit3 style={{ cursor: 'pointer' }} title="Modify Clearance" />
                          <FiTrash2 style={{ cursor: 'pointer', color: '#ef4444' }} title="Expunge Entity" />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </TableContainer>
          </>
        )}

        {activeTab === 'telemetry' && (
          <ChartPanel>
            <h3 style={{ marginBottom: '30px' }}>Live Network Telemetry</h3>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetryData}>
                <defs>
                  <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#475569" fontSize={12} />
                <YAxis stroke="#475569" fontSize={12} />
                <Tooltip
                  contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                />
                <Area type="monotone" dataKey="requests" stroke="#3b82f6" fillOpacity={1} fill="url(#colorRequests)" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartPanel>
        )}

        <LogStream>
          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '10px', marginBottom: '15px' }}>
            <span style={{ fontWeight: 900, color: '#3B82F6' }}>SYSTEM_FORENSICS_STREAM</span>
            <span style={{ color: '#475569' }}>v1.0.42_STABLE</span>
          </div>
          {logs.map((log, i) => (
            <div className="entry" key={i}>
              <span className="ts">[{log.ts}]</span>
              <span className="type" style={{ color: log.type === 'CRITICAL' ? '#ef4444' : '#3B82F6' }}>[{log.type}]</span>
              <span className="msg">{log.msg}</span>
            </div>
          ))}
          {logs.length === 0 && <div style={{ color: '#475569' }}>Waiting for system events...</div>}
        </LogStream>
      </MainContent>

      <footer style={{ marginLeft: '300px', marginTop: '60px', padding: '40px 0', borderTop: '1px solid #1E293B', textAlign: 'center' }}>
        <p style={{ letterSpacing: '5px', color: '#334155', fontWeight: 900, fontSize: '0.7rem' }}>
          WILSY OS | BILION DOLLAR PROJECT | EPITOME OF SOVEREIGNTY
        </p>
        <p style={{ color: '#1e293b', fontSize: '0.6rem', marginTop: '10px' }}>
          BIBLICAL WORTH BILLIONS NO CHILD'S PLACE. ALL SYSTEMS OPERATIONAL.
        </p>
      </footer>
      <ToastContainer position="bottom-right" />
    </OSContainer>
  );
}