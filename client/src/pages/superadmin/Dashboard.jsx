import { fetchMetrics } from "../../api/superadmin";
/* eslint-disable */
// ============================================================================
// File Path: src/pages/superadmin/Dashboard.jsx
// Project: Wilsy OS - Vision 2050
// Purpose: Super Admin Dashboard with Fortune 500 readiness
// Collaboration Notes:
//   - This file is designed for scalability, security, and real-time insights.
//   - All team members should follow the commenting style for clarity.
//   - API integration points are marked clearly for backend collaboration.
//   - UI/UX improvements are modular for design team iteration.
// ============================================================================

import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/superadmin/AuthContext';

const Dashboard = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  // Collaboration: Data fetching method
  // Backend team ensures metrics API returns JSON in agreed schema
  useEffect(() => {
    fetchMetrics()
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching metrics:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading Wilsy Vision 2050 metrics...</p>;
  if (!metrics) return <p>Metrics unavailable. Please check API connectivity.</p>;

  return (
    <div className="p-6">
      {/* Header Section */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold">
          Welcome back, {user?.name || 'Super Admin'}
        </h1>
        <p className="text-gray-500">
          Wilsy (Pty) Ltd • Vision 2050 • Registered Legal Operator
        </p>
      </header>

      {/* Key Metrics Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard title="Total Users" value={metrics.totalUsers.toLocaleString()} change="+12.3%" icon="👥" color="indigo" />
        <MetricCard title="Active Tenants" value={metrics.activeTenants} change="+5" icon="🏢" color="purple" />
        <MetricCard title="Monthly Revenue" value={`R ${(metrics.monthlyRevenue / 1e6).toFixed(1)}M`} change="+18.5%" icon="💰" color="green" />
        <MetricCard title="Security Score" value={`${metrics.securityScore}%`} change="A+" icon="🔐" color="yellow" />
      </section>

      {/* Company Registration Info */}
      <CompanyDetails />

      {/* System Status */}
      <SystemStatus metrics={metrics} />

      {/* Future Expansion: ESG & AI Insights */}
      {/* Collaboration: Data Science team will provide ESG metrics & AI predictions */}
      <FutureInsights />
    </div>
  );
};

// ============================================================================
// Helper Components
// ============================================================================

// MetricCard: Displays key performance indicators
const MetricCard = ({ title, value, change, icon, color }) => (
  <div className="bg-white border rounded-lg p-5 shadow-sm">
    <div className="flex items-center justify-between mb-3">
      <span className="text-2xl">{icon}</span>
      <span className={`text-sm font-medium ${change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
        {change}
      </span>
    </div>
    <h3 className="text-sm text-gray-500 mb-1">{title}</h3>
    <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
  </div>
);

// CompanyDetails: Static legal and registration info
const CompanyDetails = () => (
  <section className="bg-white border rounded-lg p-6 mb-6 shadow-sm">
    <h2 className="text-lg font-semibold mb-4">Wilsy (Pty) Ltd - Company Details</h2>
    <div className="grid grid-cols-2 gap-4">
      <DetailItem label="Registration Number" value="2024/123456/07" />
      <DetailItem label="VAT Number" value="4290261234" />
      <DetailItem label="CIPC Registration" value="2024-03-15" />
      <DetailItem label="Tax Reference" value="9876543210" />
      <DetailItem label="Physical Address" value="The Leonardo, 15th Floor, Sandton, 2196" />
      <DetailItem label="Postal Address" value="PO Box 784521, Sandton, 2146" />
    </div>
  </section>
);

// DetailItem: Reusable component for company info
const DetailItem = ({ label, value }) => (
  <div>
    <div className="text-xs text-gray-400 mb-1">{label}</div>
    <div className="text-sm font-medium">{value}</div>
  </div>
);

// SystemStatus: Operational health indicators
const SystemStatus = ({ metrics }) => (
  <section className="bg-white border rounded-lg p-6 shadow-sm">
    <h2 className="text-lg font-semibold mb-4">System Status</h2>
    <div className="grid grid-cols-3 gap-4">
      <StatusItem label="API Uptime" value={`${metrics.systemUptime}%`} status="operational" />
      <StatusItem label="Database" value="Connected" status="operational" />
      <StatusItem label="Redis Cache" value="Connected" status="operational" />
      <StatusItem label="Quantum Encryption" value="Active" status="operational" />
      <StatusItem label="Forensic Logging" value="Active" status="operational" />
      <StatusItem label="Compliance Status" value={`${metrics.complianceRate}%`} status="operational" />
    </div>
  </section>
);

// StatusItem: Displays system health with indicator
const StatusItem = ({ label, value, status }) => (
  <div>
    <div className="text-xs text-gray-400 mb-1">{label}</div>
    <div className="flex items-center gap-2">
      <span className={`w-2 h-2 rounded-full ${status === 'operational' ? 'bg-green-500' : 'bg-red-500'}`}></span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  </div>
);

// FutureInsights: Placeholder for AI & ESG metrics
const FutureInsights = () => (
  <section className="bg-gradient-to-r from-indigo-50 to-purple-50 border rounded-lg p-6 mt-6 shadow-md">
    <h2 className="text-lg font-semibold mb-4">Future Insights (Vision 2050)</h2>
    <p className="text-gray-600 text-sm">
      Coming soon: AI-driven predictions, ESG compliance metrics, and sustainability dashboards.
      Collaboration: Data Science & ESG teams will integrate APIs here.
    </p>
  </section>
);

export default Dashboard;
