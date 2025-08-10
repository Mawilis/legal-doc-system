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
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
`;

const SummaryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const ChartsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-bottom: 30px;

  @media (min-width: 768px) {
    flex-direction: row;
  }
`;

const ChartBox = styled.div`
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  flex: 1;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
`;

const Loading = styled.div`
  text-align: center;
  font-size: 1.5rem;
  color: #0d47a1;
`;

const ErrorMessage = styled.p`
  color: red;
  text-align: center;
  font-size: 1.2rem;
`;

const Dashboard = () => {
  const dispatch = useDispatch();
  const { metrics, charts, loading, error } = useSelector((state) => state.dashboard);
  const { documents } = useSelector((state) => state.documents);

  useEffect(() => {
    if (!metrics || !charts) dispatch(fetchDashboardData());
    if (!documents || documents.length === 0) dispatch(fetchDocuments());
  }, [dispatch, metrics, charts, documents]);

  if (loading) return <Loading>Loading Dashboard...</Loading>;
  if (error) return <ErrorMessage>{error}</ErrorMessage>;

  if (process.env.NODE_ENV === 'development') {
    console.log('[✅ Dashboard Loaded]', { metrics, charts });
  }

  return (
    <DashboardContainer>
      <SummaryGrid>
        <SummaryCard icon={<FaFileAlt />} title="Total Documents" value={metrics?.totalDocuments || 0} />
        <SummaryCard icon={<FaUsers />} title="Total Users" value={metrics?.totalUsers || 0} />
        <SummaryCard icon={<FaChartLine />} title="Monthly Growth" value={`${metrics?.monthlyGrowth || 0}%`} />
      </SummaryGrid>

      <ChartsContainer>
        <ChartBox>
          <h2>Documents Over Time</h2>
          {charts?.documentsOverTime?.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={charts.documentsOverTime}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="documents" stroke="#8884d8" activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p>No chart data available.</p>
          )}
        </ChartBox>

        <ChartBox>
          <h2>User Activity</h2>
          {charts?.userActivity?.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={charts.userActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="user" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="actions" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p>No user activity data.</p>
          )}
        </ChartBox>
      </ChartsContainer>

      <RecentDocuments documents={documents || []} />
    </DashboardContainer>
  );
};

export default Dashboard;
