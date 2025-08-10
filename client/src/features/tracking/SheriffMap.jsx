// ~/client/src/features/admin/pages/SheriffDashboard.jsx

import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import socket from '../../../services/socket'; // Use the shared socket instance
import axios from 'axios'; // Assuming an authenticated axios instance is configured
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// --- Fix for default Leaflet icon issue with bundlers ---
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// --- Styled Components for a Professional Dashboard ---

const DashboardContainer = styled.div`
  display: flex;
  height: calc(100vh - 64px); // Full viewport height minus header
  padding: 1rem;
  gap: 1rem;
`;

const SheriffListPanel = styled.div`
  width: 350px;
  flex-shrink: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
`;

const PanelHeader = styled.h2`
  font-size: 1.5rem;
  padding: 1rem;
  margin: 0;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
`;

const SheriffCard = styled.div`
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #f1f1f1;
  }
`;

const UserInfo = styled.div`
  strong {
    display: block;
    font-size: 1rem;
  }
  small {
    color: #6c757d;
  }
`;

const StatusIndicator = styled.span`
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  color: #fff;
  background-color: ${({ $active }) => ($active ? '#28a745' : '#6c757d')};
`;

const MapPanel = styled.div`
  flex-grow: 1;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  .leaflet-container {
    height: 100%;
    width: 100%;
  }
`;

/**
 * A real-time dashboard for administrators to monitor the live locations of all sheriffs.
 */
const SheriffDashboard = () => {
    // --- State Management ---
    const [locations, setLocations] = useState({}); // Use a map for efficient updates: { userId: locationData }
    const [loading, setLoading] = useState(true);

    // --- Real-time Logic ---
    useEffect(() => {
        // Connect the socket when the component mounts
        socket.connect();

        // Fetch the initial locations of all sheriffs
        const fetchInitialLocations = async () => {
            try {
                const res = await axios.get(`/api/locations`);
                const locationsMap = res.data.data.reduce((acc, loc) => {
                    acc[loc.user._id] = { ...loc, active: false }; // Initially assume not tracking
                    return acc;
                }, {});
                setLocations(locationsMap);
            } catch (err) {
                console.error("Failed to fetch initial locations", err);
            } finally {
                setLoading(false);
            }
        };

        fetchInitialLocations();

        // --- Socket Event Listeners ---
        const handleLocationUpdate = (newLoc) => {
            setLocations((prev) => ({
                ...prev,
                [newLoc.user._id]: { ...newLoc, active: true },
            }));
        };

        const handleTrackingStopped = ({ userId }) => {
            setLocations((prev) => ({
                ...prev,
                [userId]: { ...prev[userId], active: false },
            }));
        };

        socket.on('sheriff:locationUpdated', handleLocationUpdate);
        socket.on('sheriff:trackingStopped', handleTrackingStopped);

        // --- Cleanup on Unmount ---
        return () => {
            socket.off('sheriff:locationUpdated', handleLocationUpdate);
            socket.off('sheriff:trackingStopped', handleTrackingStopped);
            socket.disconnect();
        };
    }, []);

    const locationArray = Object.values(locations);

    return (
        <DashboardContainer>
            <SheriffListPanel>
                <PanelHeader>🚔 Sheriff Status</PanelHeader>
                {loading ? <p style={{ padding: '1rem' }}>Loading...</p> : (
                    <div>
                        {locationArray.map((loc) => (
                            <SheriffCard key={loc.user._id}>
                                <UserInfo>
                                    <strong>{loc.user.name}</strong>
                                    <small>Last update: {new Date(loc.updatedAt).toLocaleTimeString()}</small>
                                </UserInfo>
                                <StatusIndicator $active={loc.active}>
                                    {loc.active ? 'Tracking' : 'Inactive'}
                                </StatusIndicator>
                            </SheriffCard>
                        ))}
                    </div>
                )}
            </SheriffListPanel>

            <MapPanel>
                {/* ✅ Set the map's default center to Midrand, Gauteng */}
                <MapContainer center={[-25.989, 28.125]} zoom={12} scrollWheelZoom={true}>
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    {locationArray.filter(loc => loc.active).map((loc) => (
                        <Marker
                            key={loc.user._id}
                            position={[loc.location.coordinates[1], loc.location.coordinates[0]]}
                        >
                            <Popup>
                                <strong>{loc.user.name}</strong><br />
                                Updated: {new Date(loc.updatedAt).toLocaleTimeString()}
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </MapPanel>
        </DashboardContainer>
    );
};

export default SheriffDashboard;
