/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ Wilsy OS 2050 - SuperAdmin Page Template                                  ║
  ║ Fortune 500 Ready | POPIA §19 | SOC2 | ISO 27001                          ║
  ║ Provides a reusable scaffold for all SuperAdmin dashboard pages.          ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import React, { useState, useEffect } from 'react';
import { superAdminAPI } from '../../api/superadmin';

// Generic template component for SuperAdmin pages
const TemplatePage = ({ title, endpoint }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (endpoint) fetchData();
  }, [endpoint]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Dynamically call the endpoint provided
      const response = await superAdminAPI.get(endpoint);
      setData(response.data || response);
    } catch (err) {
      console.error(`[Citadel] Error fetching ${endpoint}:`, err);
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <h1>{title || 'SuperAdmin Page'}</h1>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && !error && (
        <pre style={{ background: '#f4f4f4', padding: '12px' }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default TemplatePage;
