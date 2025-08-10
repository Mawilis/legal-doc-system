import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { FaFileAlt } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from './LoadingSpinner';

// Styled Components
const RecentContainer = styled.section`
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const Title = styled.h2`
  font-size: 1.8rem;
  color: #333;
`;

const ViewAll = styled.button`
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #0062cc;
  }
`;

const DocumentList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const DocumentItem = styled.li`
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #f5f5f5;
  }

  &:last-child {
    border-bottom: none;
  }
`;

const DocumentIcon = styled(FaFileAlt)`
  color: #007bff;
  margin-right: 10px;
  font-size: 1.2em;
`;

const DocumentName = styled.span`
  font-size: 1rem;
  color: #333;
`;

const EmptyMessage = styled.p`
  text-align: center;
  font-style: italic;
  color: #999;
  margin-top: 20px;
`;

// ✅ RecentDocuments Component
const RecentDocuments = ({ documents = [], isLoading = false }) => {
  const navigate = useNavigate();

  const handleViewAll = () => {
    navigate('/documents');
  };

  const handleDocumentClick = (id) => {
    navigate(`/documents/${id}`);
  };

  return (
    <RecentContainer role="region" aria-label="Recent documents section">
      <Header>
        <Title>Recent Documents</Title>
        <ViewAll onClick={handleViewAll}>View All</ViewAll>
      </Header>

      {isLoading ? (
        <LoadingSpinner />
      ) : documents.length > 0 ? (
        <DocumentList>
          {documents.slice(0, 5).map((doc) => (
            <DocumentItem
              key={doc._id || doc.id}
              onClick={() => handleDocumentClick(doc._id || doc.id)}
              aria-label={`View details for ${doc.title}`}
            >
              <DocumentIcon />
              <DocumentName>{doc.title}</DocumentName>
            </DocumentItem>
          ))}
        </DocumentList>
      ) : (
        <EmptyMessage>No recent documents found.</EmptyMessage>
      )}
    </RecentContainer>
  );
};

RecentDocuments.propTypes = {
  documents: PropTypes.arrayOf(
    PropTypes.shape({
      _id: PropTypes.string,
      id: PropTypes.string,
      title: PropTypes.string.isRequired,
    })
  ),
  isLoading: PropTypes.bool,
};

export default RecentDocuments;
