import React, { useState } from 'react';

const SheriffApp = () => {
    const [location, setLocation] = useState(null);

    const getCurrentLocation = () => {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                setLocation({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                });
            },
            (error) => console.error('Error fetching location', error)
        );
    };

    return (
        <div>
            <h2>Sheriff Mobile Service</h2>
            <button onClick={getCurrentLocation}>Get Location</button>
            {location && <p>Latitude: {location.latitude}, Longitude: {location.longitude}</p>}
        </div>
    );
};

export default SheriffApp;
