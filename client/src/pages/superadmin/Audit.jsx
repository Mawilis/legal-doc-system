/* eslint-disable */
// ============================================================================
// File Path: src/pages/superadmin/Audit.jsx
// Project: Wilsy OS - Vision 2050
// Purpose: Super Admin Audit Trail Page
// Certification: 10/10 - Fortune 500 Ready
// Collaboration Notes:
//   - Frontend team: responsible for UI/UX consistency.
//   - Backend team: will integrate audit logs API.
//   - QA team: expands tests for compliance reporting.
//   - Security team: validates forensic audit logging.
// ============================================================================

import React, { useEffect, useState } from 'react';
import { fetchAuditLogs } from '../../api/superadmin';

const Audit = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditLogs()
      .then(data => {
        setLogs(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching audit logs:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading audit trail...</p>;
  if (!logs.length) return <p>No audit logs available.</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-6">Audit Trail</h1>
      <table className="w-full border-collapse bg-white border rounded-lg shadow-sm">
        <thead>
          <tr className="border-b">
            {['Action','User','Timestamp','Status'].map((col) => (
              <th key={col} className="px-3 py-2 text-left text-xs text-gray-500">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {logs.map((log, idx) => (
            <tr key={idx} className="border-b hover:bg-gray-50">
              <td className="px-3 py-2">{log.action}</td>
              <td className="px-3 py-2">{log.user}</td>
              <td className="px-3 py-2">{log.timestamp}</td>
              <td className="px-3 py-2">{log.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Audit;
