// src/features/dashboard/pages/Dashboard.jsx

import React, { useEffect } from 'react';
import styled from 'styled-components';
import SummaryCard from '../../../components/SummaryCard';
import RecentDocuments from '../../../components/RecentDocuments';
import { FaFileAlt, FaUsers, FaChartLine } from 'react-icons/fa';
import { useDispatch, useSelector } from 'react-redux';
import { fetchDashboardData } from '../reducers/dashboardSlice';
import { fetchDocuments } from '../../documents/reducers/documentSlice';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

const DashboardContainer = styled.div`
    padding: var(--spacing-lg);
    background-color: var(--background-color);
    min-height: 100vh;
`;

const SummaryGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
`;

const ChartsContainer = styled.div`
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);

    @media (min-width: var(--breakpoint-tablet)) {
        flex-direction: row;
    }
`;

const ChartBox = styled.div`
    background-color: var(--light-color);
    border: 1px solid var(--accent-color);
    border-radius: var(--border-radius);
    padding: var(--spacing-md);
    flex: 1;
    box-shadow: var(--shadow);
`;

const Loading = styled.div`
    text-align: center;
    font-size: 1.5rem;
    color: var(--primary-color);
`;

const ErrorMessage = styled.p`
    color: var(--error-color);
    text-align: center;
    font-size: 1.2rem;
`;

const Dashboard = () => {
  const dispatch = useDispatch();
  const { metrics, charts, loading, error } = useSelector((state) => state.dashboard);
  const { documents } = useSelector((state) => state.documents);

  useEffect(() => {
    dispatch(fetchDashboardData());
    dispatch(fetchDocuments());
  }, [dispatch]);

  if (loading) {
    return <Loading>Loading Dashboard...</Loading>;
  }

  if (error) {
    return <ErrorMessage>{error}</ErrorMessage>;
  }

  return (
    <DashboardContainer>
      <SummaryGrid>
        {/* Summary Cards */}
        <SummaryCard
          icon={<FaFileAlt />}
          title="Total Documents"
          value={metrics?.totalDocuments || 0} // Use optional chaining to prevent errors
        />
        <SummaryCard
          icon={<FaUsers />}
          title="Total Users"
          value={metrics?.totalUsers || 0}
        />
        <SummaryCard
          icon={<FaChartLine />}
          title="Monthly Growth"
          value={`${metrics?.monthlyGrowth || 0}%`}
        />
        {/* Add more summary cards as needed */}
      </SummaryGrid>

      <ChartsContainer>
        {/* Charts */}
        <ChartBox>
          <h2>Documents Created Over Time</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={charts?.documentsOverTime || []}> {/* Provide default empty array */}
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="documents" stroke="#8884d8" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartBox>
        <ChartBox>
          <h2>User Activity</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={charts?.userActivity || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="user" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="actions" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </ChartBox>
      </ChartsContainer>

      {/* Recent Documents */}
      <RecentDocuments documents={documents} />
    </DashboardContainer>
  );
};

export default Dashboard;