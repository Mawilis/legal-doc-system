// ~/client/src/features/documents/pages/Documents.jsx
import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { apiGet } from '../../../services/apiService';
import { FaSearch, FaPlus, FaFileAlt, FaEye, FaPen } from 'react-icons/fa';

// ==========================================
// 🎨 ENTERPRISE STYLES
// ==========================================
const Container = styled.div`
  padding: 40px;
  background-color: #f8f9fa;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, sans-serif;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
`;

const TitleBlock = styled.div`
  h1 { font-size: 2rem; color: #1a202c; margin: 0; font-weight: 800; letter-spacing: -0.02em; }
  p { color: #718096; margin-top: 5px; font-size: 1rem; }
`;

const Controls = styled.div`
  display: flex;
  gap: 15px;
  align-items: center;
`;

const SearchBox = styled.div`
  position: relative;
  width: 300px;
  
  input {
    width: 100%;
    padding: 12px 12px 12px 40px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.95rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    transition: all 0.2s;
    box-sizing: border-box; 

    &:focus {
      outline: none;
      border-color: #3182ce;
      box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
    }
  }

  svg {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: #a0aec0;
  }
`;

const PrimaryButton = styled.button`
  background: #3182ce;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  box-shadow: 0 4px 6px rgba(49, 130, 206, 0.2);

  &:hover {
    background: #2b6cb0;
    transform: translateY(-1px);
  }
`;

// --- Table Styles ---
const TableWrapper = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
  overflow: hidden;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  
  th {
    background: #f7fafc;
    padding: 16px 24px;
    text-align: left;
    font-size: 0.8rem;
    font-weight: 700;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #e2e8f0;
  }

  td {
    padding: 16px 24px;
    border-bottom: 1px solid #edf2f7;
    color: #2d3748;
    font-size: 0.95rem;
    vertical-align: middle;
  }

  tr:last-child td { border-bottom: none; }
  tr:hover td { background-color: #f8fafc; }
`;

// ✅ FIX: Using transient prop $status (standard practice)
const StatusPill = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 700;
  
  ${props => {
    switch (props.$status) {
      case 'Served': return `background: #c6f6d5; color: #22543d;`;
      case 'Non-Service': return `background: #fed7d7; color: #822727;`;
      case 'Pending': return `background: #fefcbf; color: #744210;`;
      default: return `background: #edf2f7; color: #4a5568;`;
    }
  }}
`;

const UrgencyTag = styled.span`
  color: #e53e3e;
  font-weight: 700;
  font-size: 0.75rem;
  background: #fff5f5;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #feb2b2;
  margin-left: 8px;
`;

const ActionButton = styled.button`
  background: none;
  border: 1px solid #e2e8f0;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: #4a5568;
  font-size: 0.85rem;
  font-weight: 500;
  margin-right: 8px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;

  &:hover {
    background: #edf2f7;
    color: #3182ce;
    border-color: #cbd5e0;
  }
`;

// ==========================================
// 🚀 LOGIC COMPONENT
// ==========================================
const Documents = () => {
  const navigate = useNavigate();
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // 1. Fetch Documents
  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const response = await apiGet('/documents');
        // Robust handling for { data: [...] } vs [...]
        let data = response.data || response;
        if (data.documents) data = data.documents;
        if (Array.isArray(data)) setDocs(data);
        else setDocs([]);
      } catch (error) {
        console.error("Failed to fetch docs", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, []);

  // 2. Filter Logic (CRITICAL BUG FIX)
  const filteredDocs = useMemo(() => {
    // Optimization: Skip loop if search is empty
    if (!searchTerm) return docs;

    const lowerTerm = searchTerm.toLowerCase();

    return docs.filter(doc => {
      // ✅ FIX: Safe access using (val || '') prevents "undefined.includes" crash
      const matchCase = (doc.caseNumber || '').toLowerCase().includes(lowerTerm);
      const matchPlaintiff = (doc.plaintiff || '').toLowerCase().includes(lowerTerm);
      const matchDefendant = (doc.defendant || '').toLowerCase().includes(lowerTerm);
      const matchType = (doc.type || '').toLowerCase().includes(lowerTerm);

      return matchCase || matchPlaintiff || matchDefendant || matchType;
    });
  }, [docs, searchTerm]);

  if (loading) return <div style={{ padding: '50px', textAlign: 'center' }}>Loading Registry...</div>;

  return (
    <Container>
      <Header>
        <TitleBlock>
          <h1>Case Registry</h1>
          <p>Manage legal instructions and track service returns.</p>
        </TitleBlock>

        <Controls>
          <SearchBox>
            <FaSearch />
            <input
              placeholder="Search cases, parties..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </SearchBox>
          <PrimaryButton onClick={() => navigate('/documents/new')}>
            <FaPlus /> New Instruction
          </PrimaryButton>
        </Controls>
      </Header>

      <TableWrapper>
        <Table>
          <thead>
            <tr>
              <th>Case Number</th>
              <th>Document Type</th>
              <th>Parties</th>
              <th>Service Address</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredDocs.length > 0 ? (
              filteredDocs.map(doc => (
                <tr key={doc._id}>
                  <td>
                    <strong>{doc.caseNumber}</strong>
                    {doc.urgency === 'Urgent' && <UrgencyTag>URGENT</UrgencyTag>}
                  </td>
                  <td>{doc.type}</td>
                  <td>
                    <div style={{ fontSize: '0.9rem', fontWeight: '600' }}>{doc.plaintiff}</div>
                    <div style={{ fontSize: '0.8rem', color: '#718096' }}>vs {doc.defendant}</div>
                  </td>
                  <td style={{ maxWidth: '250px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {doc.address}
                  </td>
                  <td>
                    <StatusPill $status={doc.status}>{doc.status}</StatusPill>
                  </td>
                  <td>
                    <ActionButton onClick={() => navigate(`/documents/${doc._id}`)}>
                      <FaEye /> View
                    </ActionButton>
                    <ActionButton onClick={() => navigate(`/documents/${doc._id}/edit`)}>
                      <FaPen /> Edit
                    </ActionButton>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '60px', color: '#a0aec0' }}>
                  <FaFileAlt size={40} style={{ marginBottom: '15px', opacity: 0.5 }} />
                  <div>No instructions found matching your search.</div>
                </td>
              </tr>
            )}
          </tbody>
        </Table>
      </TableWrapper>
    </Container>
  );
};

export default Documents;