import React, { useState, useEffect } from 'react';
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
const Dashboard = styled.div`
  display: grid;
  grid-template-columns: 350px 1fr;
  height: 100vh;
  font-family: 'Inter', sans-serif;
`;

const Sidebar = styled.div`
  background: #fff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  z-index: 40; 
  box-shadow: 2px 0 10px rgba(0,0,0,0.05);
  overflow: hidden;
`;

const Header = styled.div`
  padding: 20px;
  background: #0f172a;
  color: white;
`;

const List = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
`;

const JobCard = styled.div`
  padding: 15px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 4px solid ${props => props.color};
  
  &:hover { background: #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
`;

const Badge = styled.span`
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  background: ${props => props.bg};
  color: ${props => props.fg};
`;

const MapView = styled.div`
  position: relative;
  height: 100vh;
  width: 100%;
`;

const EmptyState = styled.div`
    padding: 40px;
    text-align: center;
    color: #64748b;
    font-size: 0.9rem;
`;

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
