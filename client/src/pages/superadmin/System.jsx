/* eslint-disable */
// ============================================================================
// File Path: src/pages/superadmin/System.jsx
// Project: Wilsy OS - Vision 2050
// Purpose: Super Admin System Settings Page
// Certification: 10/10 - Fortune 500 Ready
// Collaboration Notes:
//   - Frontend team: responsible for UI/UX consistency.
//   - Backend team: will integrate system configuration API.
//   - QA team: expands tests for system toggles and settings.
//   - Security team: validates secure configuration changes.
// ============================================================================

import React, { useEffect, useState } from 'react';
import { fetchSystemSettings } from '../../api/superadmin';

const System = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemSettings()
      .then(data => {
        setSettings(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching system settings:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading system settings...</p>;
  if (!settings) return <p>No system settings available.</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-6">System Settings</h1>
      <div className="bg-white border rounded-lg p-5 shadow-sm">
        {Object.entries(settings).map(([key, value]) => (
          <div key={key} className="flex justify-between py-2 border-b">
            <span className="font-medium">{key}</span>
            <span className="text-gray-600">{String(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default System;
