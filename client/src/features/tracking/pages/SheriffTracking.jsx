import React from 'react';
import SheriffMap from '../SheriffMap';

export default function SheriffTracking() {
  return (
    <div style={{ padding: 16 }}>
      <h2>Sheriff Tracking</h2>
      <p style={{ marginTop: 8, color: '#555' }}>
        Live positions, recent pings, and geo-events.
      </p>
      <div style={{ marginTop: 16 }}>
        <SheriffMap />
      </div>
    </div>
  );
}
