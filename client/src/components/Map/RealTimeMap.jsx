import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const RealTimeMap = ({ locations }) => {
    return (
        <MapContainer center={[-26.2, 28.04]} zoom={10} style={{ height: '500px', width: '100%' }}>
            <TileLayer
                attribution='&copy; OpenStreetMap contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {locations.map(({ userId, coords }) => (
                <Marker key={userId} position={[coords.latitude, coords.longitude]}>
                    <Popup>
                        <b>User:</b> {userId}<br />
                        <b>Lat:</b> {coords.latitude}<br />
                        <b>Lng:</b> {coords.longitude}
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
};

export default RealTimeMap;
