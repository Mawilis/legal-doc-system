import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { FiCheckCircle, FiShield, FiClock } from 'react-icons/fi';

const Container = styled.div`
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  font-family: 'Inter', sans-serif;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  color: #0f172a;
  
  h3 { margin: 0; font-size: 1rem; }
  svg { color: #3b82f6; }
`;

const Timeline = styled.div`
  position: relative;
  padding-left: 20px;
  border-left: 2px solid #e2e8f0;
`;

const Event = styled.div`
  position: relative;
  margin-bottom: 25px;
  padding-left: 15px;
  
  &:last-child { margin-bottom: 0; }
  
  &::before {
    content: '';
    position: absolute;
    left: -26px;
    top: 5px;
    width: 10px;
    height: 10px;
    background: #10b981;
    border: 2px solid #fff;
    border-radius: 50%;
    box-shadow: 0 0 0 2px #10b981;
  }
`;

const Meta = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 4px;
`;

const Description = styled.div`
  font-weight: 500;
  color: #334155;
  font-size: 0.9rem;
`;

const Hash = styled.div`
  font-family: monospace;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 4px;
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
`;

const Empty = styled.div`
    color: #94a3b8;
    font-style: italic;
    font-size: 0.9rem;
`;

export default function AuditTrail() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    // Fetch directly from the Gateway (Port 3001) which proxies to Ledger (Port 6000)
    fetch('http://localhost:3001/api/ledger/events')
      .then(res => res.json())
      .then(data => setEvents(data))
      .catch(err => console.error("Audit Fetch Failed:", err));
  }, []);

  return (
    <Container>
      <Header>
        <FiShield size={20} />
        <h3>Immutable Chain of Custody</h3>
      </Header>

      <Timeline>
        {events.length === 0 && <Empty>No blockchain records found.</Empty>}
        
        {events.map((ev) => (
          <Event key={ev.hash}>
            <Meta>
              <span><FiClock style={{marginRight:5}} />{new Date(ev.createdAt).toLocaleString()}</span>
              <span>Block #{ev.sequence}</span>
            </Meta>
            <Description>{ev.description || ev.eventType}</Description>
            <Hash>SHA-256: {ev.hash.substring(0, 40)}...</Hash>
          </Event>
        ))}
      </Timeline>
    </Container>
  );
}
