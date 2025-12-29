import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { useSelector } from 'react-redux';
import styled, { keyframes } from 'styled-components';
import { apiGet } from '../../../services/apiService';
import { useNavigate } from 'react-router-dom';

// ✅ CORRECT PATH: Go up 3 levels from 'pages' -> 'dashboard' -> 'features' -> 'src'
import DocumentDashboard from '../../../components/dashboard/DocumentDashboard';
import '../../../styles/dashboard.css';

// ==============================================================================
// 🎨 STYLED COMPONENTS (Fully Defined)
// ==============================================================================

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const Container = styled.div`
  padding: 2.5rem;
  background-color: #f8f9fa;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1a202c;
  animation: ${fadeIn} 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
`;

const HeaderSection = styled.div`
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-bottom: 3rem; padding-bottom: 1.5rem; border-bottom: 1px solid #e2e8f0;
`;

const TitleGroup = styled.div`
  display: flex; flex-direction: column; gap: 8px;
  h1 { font-size: 2.25rem; font-weight: 800; color: #2d3748; margin: 0; }
  .subtitle { font-size: 1rem; color: #718096; font-weight: 500; display: flex; align-items: center; gap: 8px; }
`;

const RoleBadge = styled.span`
  background-color: #2d3748; color: white; padding: 4px 12px;
  border-radius: 50px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
`;

const ActionToolbar = styled.div` display: flex; gap: 12px; align-items: center; `;

const ButtonBase = styled.button`
  display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px;
  border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s ease;
  &:hover { transform: translateY(-1px); }
`;

const PrimaryButton = styled(ButtonBase)`
  background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%); color: white;
  box-shadow: 0 4px 6px rgba(49, 130, 206, 0.2);
`;

const SecondaryButton = styled(ButtonBase)`
  background: white; color: #4a5568; border: 1px solid #e2e8f0;
  &:hover { background: #f7fafc; }
`;

const MetricsGrid = styled.div`
  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;
`;

const StatCard = styled.div`
  background: white; padding: 2rem; border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-top: 5px solid ${props => props.$accent || '#cbd5e0'};
`;

const CardValue = styled.div` font-size: 2.75rem; font-weight: 800; color: #2d3748; margin: 1rem 0; `;
const CardLabel = styled.h3` font-size: 0.8rem; font-weight: 700; color: #a0aec0; text-transform: uppercase; margin: 0;`;

// ==============================================================================
// 🚀 MAIN COMPONENT
// ==============================================================================

export default function Dashboard() {
  const { user } = useSelector((state) => state.auth);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ recentActivity: [], metrics: {}, overview: {} });

  // 1. DATA SYNC
  const loadDashboard = useCallback(async () => {
    try {
      const response = await apiGet('/dashboard');
      const data = response.data || response;
      setStats({
        overview: data.overview || {},
        metrics: data.metrics || {},
        recentActivity: data.recentActivity || [],
        role: data.role
      });
    } catch (error) {
      console.error("Dashboard Sync Failed:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  // 2. DATA TRANSFORMATION FOR TABLE
  const formattedDocs = useMemo(() => {
    return (stats.recentActivity || []).map(doc => ({
      caseNumber: doc.caseNumber || 'Pending',
      documentType: doc.subType || doc.category,
      currentStatus: doc.status || 'Draft',
      parties: doc.litigationDetails?.plaintiff
        ? `${doc.litigationDetails.plaintiff} v ${doc.litigationDetails.defendant}`
        : (doc.agreementDetails?.partyA || '-'),
      events: [
        { status: 'Created', timestamp: doc.createdAt },
        ...(doc.status !== 'Draft' ? [{ status: doc.status, timestamp: doc.updatedAt }] : [])
      ]
    }));
  }, [stats.recentActivity]);

  if (loading) return <Container>Loading Analytics...</Container>;

  return (
    <Container>
      {/* HEADER */}
      <HeaderSection>
        <TitleGroup>
          <h1>System Overview</h1>
          <div className="subtitle">
            <RoleBadge>{user?.role || 'User'}</RoleBadge>
            <span>• {user?.email}</span>
          </div>
        </TitleGroup>
        <ActionToolbar>
          <SecondaryButton onClick={() => navigate('/documents')}>Search</SecondaryButton>
          <PrimaryButton onClick={() => navigate('/documents/new')}>+ New Instruction</PrimaryButton>
        </ActionToolbar>
      </HeaderSection>

      {/* METRICS */}
      <MetricsGrid>
        <StatCard $accent="#3182ce">
          <CardLabel>Total Instructions</CardLabel>
          <CardValue>{stats.metrics?.totalInstructions || 0}</CardValue>
        </StatCard>
        <StatCard $accent="#38a169">
          <CardLabel>Completed / Served</CardLabel>
          <CardValue>{stats.metrics?.servedSuccess || 0}</CardValue>
        </StatCard>
        <StatCard $accent="#e53e3e">
          <CardLabel>Pending Action</CardLabel>
          <CardValue>{stats.metrics?.pending || 0}</CardValue>
        </StatCard>
      </MetricsGrid>

      {/* 🔥 THE NEW TABLE (This was causing the error, now fixed) */}
      <DocumentDashboard documents={formattedDocs} />
    </Container>
  );
}