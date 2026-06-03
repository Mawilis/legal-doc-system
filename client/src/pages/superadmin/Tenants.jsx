import React, { useState, useEffect } from 'react';
import { superAdminAPI } from '../../api/superadmin';
import { useTenants } from '../../contexts/tenantContext';

const Tenants = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const { tenants: contextTenants, fetchTenants: fetchContextTenants, loading, error } = useTenants();
  const [localTenants, setLocalTenants] = useState([]);

  // Real South African law firms as tenants
  const mockTenants = [
    { id: 'dentons-001', name: 'Dentons South Africa', registration: '2001/012345/21', users: 245, plan: 'Enterprise', status: 'Active', revenue: 'R 450K', jurisdiction: 'ZA' },
    { id: 'cliffedekker-002', name: 'Cliffe Dekker Hofmeyr', registration: '1998/045678/23', users: 189, plan: 'Enterprise', status: 'Active', revenue: 'R 380K', jurisdiction: 'ZA' },
    { id: 'webberwentzel-003', name: 'Webber Wentzel', registration: '2005/078912/18', users: 312, plan: 'Ultra', status: 'Active', revenue: 'R 620K', jurisdiction: 'ZA' },
    { id: 'ensafrica-004', name: 'ENSafrica', registration: '2003/056789/14', users: 278, plan: 'Enterprise', status: 'Active', revenue: 'R 510K', jurisdiction: 'ZA' },
    { id: 'bowmans-005', name: 'Bowmans', registration: '2007/089123/27', users: 156, plan: 'Professional', status: 'Active', revenue: 'R 290K', jurisdiction: 'ZA' },
    { id: 'werksmans-006', name: 'Werksmans', registration: '2002/034567/19', users: 134, plan: 'Professional', status: 'Suspended', revenue: 'R 0', jurisdiction: 'ZA' },
    { id: 'nortonrose-007', name: 'Norton Rose Fulbright SA', registration: '2008/092345/31', users: 198, plan: 'Enterprise', status: 'Active', revenue: 'R 360K', jurisdiction: 'ZA' },
    { id: 'allenov-008', name: 'Allen & Overy SA', registration: '2010/067891/42', users: 87, plan: 'Business', status: 'Active', revenue: 'R 150K', jurisdiction: 'ZA' },
  ];

  useEffect(() => {
    // Use either context tenants or mock data
    if (contextTenants && contextTenants.length > 0) {
      setLocalTenants(contextTenants);
    } else {
      setLocalTenants(mockTenants);
    }
  }, [contextTenants]);

  const filteredTenants = localTenants.filter(tenant =>
    tenant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tenant.registration.includes(searchTerm)
  );

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 600 }}>Tenant Management</h1>
        <button style={{
          padding: '10px 20px',
          backgroundColor: '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontWeight: 500
        }}>
          + Onboard New Tenant
        </button>
      </div>

      {/* Stats Summary */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <StatCard label="Total Tenants" value={localTenants.length.toString()} />
        <StatCard label="Active Tenants" value={localTenants.filter(t => t.status === 'Active').length.toString()} />
        <StatCard label="Total Monthly Revenue" value="R 2.76M" />
        <StatCard label="Avg. Users/Tenant" value="199" />
      </div>

      {/* Search Bar */}
      <div style={{ marginBottom: '24px' }}>
        <input
          type="text"
          placeholder="Search tenants by name or registration number..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            padding: '12px 16px',
            backgroundColor: 'white',
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            color: '#333',
            fontSize: '14px'
          }}
        />
      </div>

      {/* Tenants Table */}
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #e0e0e0',
        borderRadius: '12px',
        overflow: 'hidden'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #e0e0e0' }}>
              <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', color: '#999' }}>Law Firm</th>
              <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', color: '#999' }}>Reg Number</th>
              <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', color: '#999' }}>Users</th>
              <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', color: '#999' }}>Plan</th>
              <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', color: '#999' }}>Monthly Revenue</th>
              <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', color: '#999' }}>Status</th>
              <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', color: '#999' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredTenants.map((tenant) => (
              <tr key={tenant.id} style={{ borderBottom: '1px solid #e0e0e0' }}>
                <td style={{ padding: '16px', fontWeight: 500 }}>{tenant.name}</td>
                <td style={{ padding: '16px' }}>{tenant.registration}</td>
                <td style={{ padding: '16px' }}>{tenant.users}</td>
                <td style={{ padding: '16px' }}>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    backgroundColor: tenant.plan === 'Ultra' ? 'rgba(139, 92, 246, 0.1)' :
                                   tenant.plan === 'Enterprise' ? 'rgba(16, 185, 129, 0.1)' :
                                   'rgba(59, 130, 246, 0.1)',
                    color: tenant.plan === 'Ultra' ? '#8b5cf6' :
                           tenant.plan === 'Enterprise' ? '#10b981' :
                           '#3b82f6'
                  }}>
                    {tenant.plan}
                  </span>
                </td>
                <td style={{ padding: '16px' }}>{tenant.revenue}</td>
                <td style={{ padding: '16px' }}>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    backgroundColor: tenant.status === 'Active' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: tenant.status === 'Active' ? '#10b981' : '#ef4444'
                  }}>
                    {tenant.status}
                  </span>
                </td>
                <td style={{ padding: '16px' }}>
                  <button style={{ marginRight: '8px', background: 'none', border: 'none', color: '#667eea', cursor: 'pointer' }}>Manage</button>
                  <button style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>Suspend</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StatCard = ({ label, value }) => (
  <div style={{
    backgroundColor: 'white',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '16px'
  }}>
    <div style={{ fontSize: '12px', color: '#999', marginBottom: '4px' }}>{label}</div>
    <div style={{ fontSize: '20px', fontWeight: 600, color: '#667eea' }}>{value}</div>
  </div>
);

export default Tenants;
