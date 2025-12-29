import React from 'react';
import styled from 'styled-components';
import { FiShield, FiTrendingUp, FiCheckCircle } from 'react-icons/fi';

const MasterpieceCard = styled.div`
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  padding: 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
`;

const BrandWatermark = styled.div`
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 5rem;
  font-weight: 900;
  color: rgba(15, 23, 42, 0.03);
  text-transform: lowercase;
  pointer-events: none;
`;

const Badge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f0fdf4;
  color: #166534;
  padding: 6px 12px;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 16px;
`;

export default function WilsyIntelligenceCard({ intelligence }) {
  if (intelligence.loading) return <div style={{padding: '20px', color: '#94a3b8'}}>Synchronizing Wilsy Intelligence...</div>;

  return (
    <MasterpieceCard>
      <BrandWatermark>wilsy</BrandWatermark>
      
      <Badge><FiCheckCircle /> Verified by Wilsy Pty Ltd</Badge>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase' }}>Financial Security</h4>
          <div style={{ fontSize: '1.5rem', fontWeight: '900', color: '#0f172a' }}>
            R {intelligence.billing?.total || '0.00'}
          </div>
          <p style={{ fontSize: '0.7rem', color: '#94a3b8', margin: '5px 0' }}>Current Market Rate Assessment</p>
        </div>

        <div>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase' }}>AI Risk Analysis</h4>
          <div style={{ fontSize: '1.2rem', fontWeight: '800', color: intelligence.risk?.riskLevel === 'HIGH' ? '#ef4444' : '#10b981' }}>
             {intelligence.risk?.riskLevel || 'OPTIMAL'}
          </div>
          <p style={{ fontSize: '0.7rem', color: '#94a3b8', margin: '5px 0' }}>Touching Lives through safety</p>
        </div>
      </div>

      <div style={{ marginTop: '20px', paddingTop: '15px', borderTop: '1px solid #f1f5f9' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#334155', fontWeight: '600', fontSize: '0.85rem' }}>
          <FiShield /> Ledger Proof: <span style={{ fontFamily: 'monospace', color: '#64748b' }}>{intelligence.risk?.merkleRoot?.substring(0, 16)}...</span>
        </div>
      </div>
    </MasterpieceCard>
  );
}
