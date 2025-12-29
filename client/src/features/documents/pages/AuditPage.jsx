import React from 'react';
import styled from 'styled-components';
import AuditTrail from '../components/AuditTrail';

const PageContainer = styled.div`
  padding: 40px;
  background: #f8fafc;
  min-height: 100vh;
`;

const Title = styled.h1`
  color: #0f172a;
  margin-bottom: 10px;
`;

const Subtitle = styled.p`
  color: #64748b;
  margin-bottom: 30px;
`;

export default function AuditPage() {
  return (
    <PageContainer>
      <Title>System Audit Log</Title>
      <Subtitle>Real-time view of the Immutable Ledger (Port 6000)</Subtitle>
      <AuditTrail />
    </PageContainer>
  );
}
