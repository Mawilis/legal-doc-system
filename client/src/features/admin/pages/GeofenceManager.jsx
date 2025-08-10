// ~/client/src/features/admin/pages/GeofenceManager.jsx

import React, { useState, useCallback } from 'react';
import { MapContainer, TileLayer, Polygon, useMapEvents } from 'react-leaflet';
import styled from 'styled-components';
import Button from '../../../components/atoms/Button'; // Use our masterpiece Button
import { toast } from 'react-toastify';

// --- Styled Components ---
const Container = styled.div`
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
`;

const Header = styled.h2`
  font-size: 1.8rem;
  color: #333;
  margin-top: 0;
  margin-bottom: 1rem;
`;

const ControlPanel = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  align-items: center;
`;

const MapWrapper = styled.div`
  height: 60vh;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
`;

/**
 * A helper component that captures click events on the map to draw a new geofence.
 * @param {object} props
 * @param {Function} props.onMapClick - The callback function to execute on a map click.
 */
const MapClickHandler = ({ onMapClick }) => {
    useMapEvents({
        click(e) {
            onMapClick(e.latlng);
        },
    });
    return null; // This component does not render anything itself
};

/**
 * GeofenceManager Component: An admin page for creating and viewing geofenced zones.
 */
const GeofenceManager = () => {
    // --- State Management ---
    // In a real app, `geofences` would be fetched from and saved to your backend.
    const [geofences, setGeofences] = useState([]);
    const [newFencePoints, setNewFencePoints] = useState([]);

    /**
     * Adds a new point to the geofence currently being drawn.
     * @param {L.LatLng} latlng - The latitude and longitude of the clicked point.
     */
    const handleMapClick = useCallback((latlng) => {
        setNewFencePoints((prev) => [...prev, [latlng.lat, latlng.lng]]);
    }, []);

    /**
     * Saves the currently drawn geofence to the state.
     */
    const handleSaveFence = () => {
        if (newFencePoints.length < 3) {
            toast.error('A geofence must have at least 3 points.');
            return;
        }
        // In a real app, you would send this to your backend API here.
        // For example: await api.geofence.create(newFencePoints);
        setGeofences((prev) => [...prev, newFencePoints]);
        setNewFencePoints([]);
        toast.success('Geofence saved successfully!');
    };

    /**
     * Clears the points for the geofence currently being drawn.
     */
    const handleClear = () => {
        setNewFencePoints([]);
    };

    return (
        <Container>
            <Header>Geofence Control Panel</Header>
            <p>Click on the map to draw a new geofence. Click at least 3 points to form a valid zone.</p>

            <MapWrapper>
                <MapContainer center={[-25.989, 28.125]} zoom={13} style={{ height: '100%', width: '100%' }}>
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    <MapClickHandler onMapClick={handleMapClick} />

                    {/* Render saved geofences */}
                    {geofences.map((fence, i) => (
                        <Polygon key={`saved-${i}`} positions={fence} pathOptions={{ color: 'blue' }} />
                    ))}

                    {/* Render the new geofence as it's being drawn */}
                    {newFencePoints.length > 0 && (
                        <Polygon positions={newFencePoints} pathOptions={{ color: 'green', dashArray: '5, 10' }} />
                    )}
                </MapContainer>
            </MapWrapper>

            <ControlPanel>
                <Button variant="success" onClick={handleSaveFence} disabled={newFencePoints.length < 3}>
                    Save Geofence
                </Button>
                <Button variant="secondary" outline onClick={handleClear} disabled={newFencePoints.length === 0}>
                    Clear Current Drawing
                </Button>
            </ControlPanel>
        </Container>
    );
};

export default GeofenceManager;
