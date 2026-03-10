/* eslint-disable */
// ============================================================================
// File Path: src/pages/superadmin/Reports.jsx
// Project: Wilsy OS - Vision 2050
// Purpose: Super Admin Reports Dashboard
// Certification: 10/10 - Fortune 500 Ready
// Collaboration Notes:
//   - Frontend team: responsible for UI/UX consistency.
//   - Backend team: will integrate financial and operational reports API.
//   - QA team: expands tests for reporting accuracy.
//   - Finance team: validates compliance with reporting standards.
// ============================================================================

import React, { useEffect, useState } from 'react';
import { fetchReports } from '../../api/superadmin';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports()
      .then(data => {
        setReports(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching reports:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading reports...</p>;
  if (!reports.length) return <p>No reports available.</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-6">Reports Dashboard</h1>
      <div className="bg-white border rounded-lg p-5 shadow-sm">
        <ul className="list-disc pl-5">
          {reports.map((report, idx) => (
            <li key={idx} className="mb-2">
              <span className="font-medium">{report.title}</span> - <span className="text-gray-600">{report.date}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Reports;
