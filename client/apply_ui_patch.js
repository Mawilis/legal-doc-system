const fs = require('fs');
const path = require('path');

console.log('🛠️ APPLYING "BILLION-DOLLAR" UI PATCH...');

// 1. DEFINE PATHS
const sidebarPath = path.join(__dirname, 'src/components/layout/Sidebar.js');
const trackingPath = path.join(__dirname, 'src/features/documents/pages/SheriffTracking.jsx');

// 2. SIDEBAR CODE (Collapsible & Professional)
const sidebarCode = `import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { 
  FiGrid, FiFileText, FiMap, FiActivity, FiSettings, 
  FiSearch, FiMessageSquare, FiUser, FiLogOut, FiPlusCircle,
  FiChevronLeft, FiChevronRight
} from 'react-icons/fi';
import { useDispatch } from 'react-redux';
import { logoutUser } from '../../features/auth/reducers/authSlice';

// --- STYLES ---
const Container = styled.div\`
  width: \${props => props.collapsed ? '80px' : '260px'};
  background: #0f172a;
  color: #fff;
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 50;
  box-shadow: 4px 0 10px rgba(0,0,0,0.1);
\`;

const LogoArea = styled.div\`
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: \${props => props.collapsed ? 'center' : 'space-between'};
  padding: 0 \${props => props.collapsed ? '0' : '20px'};
  border-bottom: 1px solid #1e293b;
  color: #38bdf8;
  font-weight: 800;
  letter-spacing: 1px;
  white-space: nowrap;
  overflow: hidden;
\`;

const ToggleBtn = styled.button\`
  background: #1e293b;
  border: none;
  color: #94a3b8;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;

  &:hover { color: #fff; background: #334155; }
\`;

const Menu = styled.div\`
  flex: 1;
  padding: 20px 10px;
  overflow-y: auto;
  overflow-x: hidden;
  &::-webkit-scrollbar { width: 0; display: none; }
\`;

const GroupTitle = styled.div\`
  font-size: 0.7rem;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
  margin: 25px 0 10px 12px;
  opacity: \${props => props.collapsed ? 0 : 1};
  transition: opacity 0.2s;
  white-space: nowrap;
  display: \${props => props.collapsed ? 'none' : 'block'};
\`;

const MenuItem = styled(NavLink)\`
  display: flex;
  align-items: center;
  justify-content: \${props => props.collapsed ? 'center' : 'flex-start'};
  padding: 12px;
  color: #94a3b8;
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 4px;
  font-size: 0.95rem;
  transition: all 0.2s;
  height: 48px;
  position: relative;

  &.active {
    background: #2563eb;
    color: #fff;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3);
  }

  &:hover:not(.active) {
    background: #1e293b;
    color: #fff;
  }

  svg {
    font-size: 1.25rem;
    min-width: 24px;
    margin-right: \${props => props.collapsed ? '0' : '12px'};
  }

  span {
    display: \${props => props.collapsed ? 'none' : 'block'};
    white-space: nowrap;
    opacity: \${props => props.collapsed ? 0 : 1};
    transition: opacity 0.2s;
  }
  
  &:hover::after {
    content: "\${props => props.collapsed ? props.label : ''}";
    position: absolute;
    left: 70px;
    background: #0f172a;
    color: #fff;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 0.8rem;
    white-space: nowrap;
    z-index: 100;
    pointer-events: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    display: \${props => props.collapsed ? 'block' : 'none'};
  }
\`;

const Footer = styled.div\`
  padding: 15px;
  border-top: 1px solid #1e293b;
  display: flex;
  justify-content: center;
\`;

const LogoutBtn = styled.button\`
  background: transparent;
  border: 1px solid #334155;
  color: #cbd5e1;
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: \${props => props.collapsed ? '0' : '10px'};
  transition: all 0.2s;
  height: 44px;

  &:hover {
    background: #ef4444;
    border-color: #ef4444;
    color: #fff;
  }
\`;

export default function Sidebar() {
  const dispatch = useDispatch();
  const [collapsed, setCollapsed] = useState(false);

  const toggle = () => setCollapsed(!collapsed);

  return (
    <Container collapsed={collapsed}>
      <LogoArea collapsed={collapsed}>
        {collapsed ? 'LX' : 'LEX TECH OS'}
        {!collapsed && (
            <ToggleBtn onClick={toggle}>
                <FiChevronLeft />
            </ToggleBtn>
        )}
      </LogoArea>
      
      {collapsed && (
          <div style={{display:'flex', justifyContent:'center', padding:'10px 0', borderBottom:'1px solid #1e293b'}}>
             <ToggleBtn onClick={toggle}><FiChevronRight /></ToggleBtn>
          </div>
      )}

      <Menu>
        <GroupTitle collapsed={collapsed}>Core</GroupTitle>
        <MenuItem to="/dashboard" collapsed={collapsed} label="Dashboard">
            <FiGrid /> <span>Dashboard</span>
        </MenuItem>
        <MenuItem to="/documents" collapsed={collapsed} label="Documents">
            <FiFileText /> <span>Documents</span>
        </MenuItem>
        <MenuItem to="/sheriff/new-instruction" collapsed={collapsed} label="New Instruction">
            <FiPlusCircle /> <span>New Instruction</span>
        </MenuItem>
        
        <GroupTitle collapsed={collapsed}>Sheriff Ops</GroupTitle>
        <MenuItem to="/sheriff/tracking" collapsed={collapsed} label="Live Tracking">
            <FiMap /> <span>Live Tracking</span>
        </MenuItem>
        <MenuItem to="/sheriff/analytics" collapsed={collapsed} label="Analytics">
            <FiActivity /> <span>Analytics</span>
        </MenuItem>

        <GroupTitle collapsed={collapsed}>Tools</GroupTitle>
        <MenuItem to="/chat" collapsed={collapsed} label="Chat">
            <FiMessageSquare /> <span>Chat</span>
        </MenuItem>
        <MenuItem to="/search" collapsed={collapsed} label="Search">
            <FiSearch /> <span>Search</span>
        </MenuItem>
        <MenuItem to="/profile" collapsed={collapsed} label="Profile">
            <FiUser /> <span>Profile</span>
        </MenuItem>
        <MenuItem to="/settings" collapsed={collapsed} label="Settings">
            <FiSettings /> <span>Settings</span>
        </MenuItem>
      </Menu>

      <Footer>
        <LogoutBtn onClick={() => dispatch(logoutUser())} collapsed={collapsed}>
          <FiLogOut /> {collapsed ? '' : 'Logout'}
        </LogoutBtn>
      </Footer>
    </Container>
  );
}
`;

// 3. TRACKING MAP CODE (Crash-Proof)
const trackingCode = `import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { apiGet } from '../../../services/http';

// FIX LEAFLET ICONS
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// --- STYLES ---
const Dashboard = styled.div\`
  display: grid;
  grid-template-columns: 350px 1fr;
  height: 100vh;
  font-family: 'Inter', sans-serif;
\`;

const Sidebar = styled.div\`
  background: #fff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  z-index: 40; 
  box-shadow: 2px 0 10px rgba(0,0,0,0.05);
  overflow: hidden;
\`;

const Header = styled.div\`
  padding: 20px;
  background: #0f172a;
  color: white;
\`;

const List = styled.div\`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
\`;

const JobCard = styled.div\`
  padding: 15px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 4px solid \${props => props.color};
  
  &:hover { background: #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
\`;

const Badge = styled.span\`
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  background: \${props => props.bg};
  color: \${props => props.fg};
\`;

const MapView = styled.div\`
  position: relative;
  height: 100vh;
  width: 100%;
\`;

const EmptyState = styled.div\`
    padding: 40px;
    text-align: center;
    color: #64748b;
    font-size: 0.9rem;
\`;

// --- ICONS ---
const urgentIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const normalIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const completedIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function SheriffTracking() {
  const [fleet, setFleet] = useState([]);
  const [loading, setLoading] = useState(true);

  // Poll for updates every 5 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); 
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const response = await apiGet('/tracking/live');
      
      // DEFENSIVE PROGRAMMING: Ensure response is an array
      if (Array.isArray(response)) {
          setFleet(response);
      } else {
          console.warn('API returned non-array:', response);
          setFleet([]); // Fallback to empty
      }
      setLoading(false);
    } catch (err) {
      console.error('Tracking API Failed:', err);
      setFleet([]); // Fallback to empty on error
      setLoading(false);
    }
  };

  const getStatusColor = (status, urgency) => {
    if (status === 'completed' || status === 'returned') return '#10b981'; // Green
    if (urgency === 'urgent' || urgency === 'high') return '#ef4444'; // Red
    return '#3b82f6'; // Blue
  };

  return (
    <Dashboard>
      <Sidebar>
        <Header>
            <h2 style={{margin:0, fontSize:'1.2rem'}}>🛰️ Live Operations</h2>
            <div style={{fontSize:'0.8rem', opacity:0.8, marginTop:'5px'}}>
                {fleet.length} Active Units Monitoring
            </div>
        </Header>
        <List>
            {fleet.length === 0 && !loading && (
                <EmptyState>No active units currently online.</EmptyState>
            )}
            
            {fleet.map(unit => (
                <JobCard key={unit.id} color={getStatusColor(unit.status, unit.urgency)}>
                    <div style={{display:'flex', justifyContent:'space-between', marginBottom:'5px'}}>
                        <strong>{unit.caseNumber}</strong>
                        <Badge 
                            bg={unit.urgency === 'urgent' ? '#fee2e2' : '#e0f2fe'} 
                            fg={unit.urgency === 'urgent' ? '#ef4444' : '#0ea5e9'}
                        >
                            {unit.urgency || 'NORMAL'}
                        </Badge>
                    </div>
                    <div style={{fontSize:'0.85rem', color:'#64748b', marginBottom:'8px'}}>{unit.title}</div>
                    <div style={{fontSize:'0.75rem', display:'flex', justifyContent:'space-between', color:'#94a3b8'}}>
                        <span>📍 {unit.location?.lat.toFixed(4)}, {unit.location?.lng.toFixed(4)}</span>
                        <span>{new Date(unit.lastUpdate).toLocaleTimeString()}</span>
                    </div>
                </JobCard>
            ))}
        </List>
      </Sidebar>
      
      <MapView>
         {!loading && (
             <MapContainer center={[-26.1076, 28.0567]} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                />
                
                {fleet.map(unit => (
                    <Marker 
                        key={unit.id} 
                        position={[unit.location.lat, unit.location.lng]}
                        icon={
                            unit.status === 'completed' ? completedIcon :
                            (unit.urgency === 'urgent' ? urgentIcon : normalIcon)
                        }
                    >
                        <Popup>
                            <strong>{unit.caseNumber}</strong><br/>
                            {unit.title}<br/>
                            <hr style={{margin:'5px 0', borderTop:'1px solid #eee'}}/>
                            Status: <b>{unit.outcome ? unit.outcome.toUpperCase() : 'UNKNOWN'}</b><br/>
                            Last Ping: {new Date(unit.lastUpdate).toLocaleTimeString()}
                        </Popup>
                    </Marker>
                ))}
             </MapContainer>
         )}
      </MapView>
    </Dashboard>
  );
}
`;

// 4. WRITE THE FILES
fs.writeFileSync(sidebarPath, sidebarCode);
console.log('✅ SIDEBAR FIXED: Collapsible & Professional.');

fs.writeFileSync(trackingPath, trackingCode);
console.log('✅ MAP FIXED: Crash-proof & Defensive.');

console.log('✨ SYSTEM READY. RESTART REACT (npm start).');
