// ~/client/src/features/sheriff/pages/SheriffDashboard.jsx

import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useSelector } from 'react-redux';
import socket from '../../../services/socket'; // Use the shared socket instance
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import 'react-leaflet-cluster/dist/styles.min.css';
import L from 'leaflet';

// --- Fix for default Leaflet icon issue with bundlers ---
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// --- Helper component to keep the map centered on the user's location ---
const MapCenterUpdater = ({ position }) => {
    const map = useMap();
    useEffect(() => {
        if (position) {
            map.setView(position, map.getZoom());
        }
    }, [position, map]);
    return null;
};

/**
 * A real-time dashboard for an individual sheriff to view their own tracking status and location.
 */
const SheriffDashboard = () => {
    // --- State Management ---
    const [currentLocation, setCurrentLocation] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [isConnected, setConnected] = useState(socket.connected);
    const { user } = useSelector((state) => state.auth);

    // --- Real-time Logic ---

    // ✅ Effect #1: Manages the socket connection lifecycle.
    // This runs only once on mount and cleans up on unmount.
    useEffect(() => {
        if (!socket.connected) {
            socket.connect();
        }

        const handleConnect = () => setConnected(true);
        const handleDisconnect = () => setConnected(false);

        socket.on('connect', handleConnect);
        socket.on('disconnect', handleDisconnect);

        // Cleanup on unmount
        return () => {
            socket.off('connect', handleConnect);
            socket.off('disconnect', handleDisconnect);
            socket.disconnect();
        };
    }, []); // Empty dependency array ensures this runs only once.

    // ✅ Effect #2: Manages user-specific event listeners.
    // This effect re-runs only if the user's ID changes.
    useEffect(() => {
        // Do nothing if there's no user
        if (!user?.id) return;

        // This listener provides confirmation that the server is receiving the sheriff's location updates.
        const handleLocationUpdate = (newLoc) => {
            // We only care about updates for the currently logged-in sheriff
            if (newLoc.user._id === user.id) {
                setCurrentLocation([newLoc.location.coordinates[1], newLoc.location.coordinates[0]]);
                setLastUpdate(new Date(newLoc.updatedAt));
            }
        };

        socket.on('sheriff:locationUpdated', handleLocationUpdate);

        // Cleanup this specific listener when the component unmounts or the user.id changes.
        return () => {
            socket.off('sheriff:locationUpdated', handleLocationUpdate);
        };
    }, [user?.id]); // Depend only on the stable user ID.

    const mapPosition = currentLocation || [-25.989, 28.125]; // Default to Midrand if no location yet

    return (
        <DashboardContainer>
            <StatusPanel>
                <PanelHeader>Your Status</PanelHeader>
                <StatusContent>
                    <InfoItem>
                        <strong>Sheriff:</strong> {user?.name || 'Loading...'}
                    </InfoItem>
                    <InfoItem>
                        <strong>Connection:</strong>
                        <StatusIndicator $active={isConnected}>
                            {isConnected ? 'Connected' : 'Offline'}
                        </StatusIndicator>
                    </InfoItem>
                    <InfoItem>
                        <strong>Tracking:</strong>
                        <StatusIndicator $active={!!currentLocation}>
                            {currentLocation ? 'Broadcasting' : 'Inactive'}
                        </StatusIndicator>
                    </InfoItem>
                    {lastUpdate && (
                        <InfoItem>
                            <strong>Last Update:</strong> {lastUpdate.toLocaleTimeString()}
                        </InfoItem>
                    )}
                </StatusContent>
            </StatusPanel>

            <MapPanel>
                <MapContainer center={mapPosition} zoom={15} scrollWheelZoom={true}>
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    {/* Note: MarkerClusterGroup is not needed here as we are only showing one user */}
                    {currentLocation && (
                        <Marker position={currentLocation}>
                            <Popup>
                                <strong>Your Location</strong><br />
                                {lastUpdate && `Updated: ${lastUpdate.toLocaleTimeString()}`}
                            </Popup>
                        </Marker>
                    )}
                    <MapCenterUpdater position={currentLocation} />
                </MapContainer>
            </MapPanel>
        </DashboardContainer>
    );
};

// --- Styled Components ---
const DashboardContainer = styled.div`
  display: flex;
  height: calc(100vh - 64px);
  padding: 1rem;
  gap: 1rem;
`;
const StatusPanel = styled.div`
  width: 350px;
  flex-shrink: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
const StatusContent = styled.div`
  padding: 1rem;
`;
const InfoItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
  margin-bottom: 1rem;
  strong {
    color: #333;
  }
`;
const StatusIndicator = styled.span`
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  color: #fff;
  background-color: ${({ $active }) => ($active ? '#28a745' : '#dc3545')};
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

export default SheriffDashboard;
