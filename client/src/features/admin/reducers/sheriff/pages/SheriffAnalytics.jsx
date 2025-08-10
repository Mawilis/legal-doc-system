// ~/client/src/features/sheriff/pages/SheriffAnalytics.jsx

import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBreachLogs, setReplayPath, clearReplay } from '../reducers/sheriffSlice';
import styled from 'styled-components';
import Button from '../../../components/atoms/Button';
import LoadingSpinner from '../../../components/LoadingSpinner';

/**
 * A dashboard for analyzing historical geofence breaches and replaying user paths.
 */
const SheriffAnalytics = () => {
    const dispatch = useDispatch();
    const { breaches, replayPath, activeReplayUser, loading } = useSelector((state) => state.sheriff);

    useEffect(() => {
        dispatch(fetchBreachLogs());
    }, [dispatch]);

    const handleReplay = (userId) => {
        // Find all historical location points for the selected user to create a path
        // In a real app, you would fetch this from a dedicated endpoint: GET /api/locations/history/:userId
        const path = breaches
            .filter((b) => b.user?._id === userId)
            .map((b) => [b.coords.lat, b.coords.lng]); // Create [lat, lng] pairs

        dispatch(setReplayPath({ path, userId }));
    };

    const handleClearReplay = () => {
        dispatch(clearReplay());
    };

    // Memoize breach points to prevent re-calculation on every render
    const breachPoints = useMemo(() =>
        breaches.map((b, i) => (
            <CircleMarker
                key={i}
                center={[b.coords.lat, b.coords.lng]}
                radius={8}
                pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.8 }}
            >
                <Popup>
                    <strong>Breach by: {b.user?.name || 'Unknown'}</strong><br />
                    At: {new Date(b.timestamp).toLocaleString()}
                </Popup>
            </CircleMarker>
        )), [breaches]);

    return (
        <Container>
            <Sidebar>
                <Header>
                    <h3>🚨 Breach Logs</h3>
                    {activeReplayUser && <Button size="small" onClick={handleClearReplay}>Clear Replay</Button>}
                </Header>
                <LogList>
                    {loading && <LoadingSpinner />}
                    {breaches.map((b) => (
                        <LogItem key={b._id}>
                            <div>
                                <strong>{b.user?.name || 'Unknown User'}</strong>
                                <small>{new Date(b.timestamp).toLocaleString()}</small>
                            </div>
                            <Button size="small" outline onClick={() => handleReplay(b.user?._id)}>Replay Path</Button>
                        </LogItem>
                    ))}
                </LogList>
            </Sidebar>

            <MapWrapper>
                <MapContainer center={[-25.989, 28.125]} zoom={12} style={{ height: '100%', width: '100%' }}>
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    {breachPoints}
                    {replayPath.length > 0 && (
                        <Polyline positions={replayPath} pathOptions={{ color: 'blue', weight: 5 }} />
                    )}
                </MapContainer>
            </MapWrapper>
        </Container>
    );
};

// --- Styled Components ---
const Container = styled.div` display: flex; height: calc(100vh - 64px); `;
const Sidebar = styled.div`
  width: 350px;
  background: #fff;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e0e0e0;
`;
const Header = styled.div`
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    h3 { margin: 0; }
`;
const LogList = styled.ul`
    list-style: none;
    padding: 0;
    margin: 0;
    overflow-y: auto;
    flex-grow: 1;
`;
const LogItem = styled.li`
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    div {
        display: flex;
        flex-direction: column;
    }
    strong { font-size: 0.95rem; }
    small { font-size: 0.8rem; color: #6c757d; }
`;
const MapWrapper = styled.div` flex: 1; `;

export default SheriffAnalytics;
