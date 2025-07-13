import React from 'react';
import styled from 'styled-components';
import { FaFileAlt } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from './LoadingSpinner';

// Styled Components
const RecentContainer = styled.div`
  background-color: #f9f9f9; // Light background color
  border: 1px solid #ddd; // Subtle border
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); // Add a subtle shadow
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const Title = styled.h2`
  font-size: 1.8rem;
  color: #333; // Darker text color
`;

const ViewAll = styled.button`
  background-color: #007bff; // Primary button color
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s ease; // Add a transition for hover effect

  &:hover {
    background-color: #0062cc; // Darker shade on hover
  }
`;

const DocumentList = styled.ul`
  list-style: none;
  padding: 0;
`;

const DocumentItem = styled.li`
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee; // Light separator
  cursor: pointer; // Add cursor pointer to indicate clickability
  transition: background-color 0.2s ease; // Add transition for hover effect

  &:hover {
    background-color: #f5f5f5; // Light background on hover
  }

  &:last-child {
    border-bottom: none;
  }
`;

const DocumentIcon = styled(FaFileAlt)`
  color: #007bff; // Primary color for the icon
  margin-right: 10px;
  font-size: 1.2em; // Slightly larger icon
`;

const DocumentName = styled.span`
  font-size: 1rem;
  color: #333;
`;

const RecentDocuments = ({ documents, isLoading }) => {
  const navigate = useNavigate();

  const handleViewAll = () => {
    navigate('/documents');
  };

  const handleDocumentClick = (id) => {
    navigate(`/documents/${id}`);
  };

  if (isLoading) {
    return (
      <RecentContainer>
        <Header>
          <Title>Recent Documents</Title>
        </Header>
        <LoadingSpinner />
      </RecentContainer>
    );
  }

  return (
    <RecentContainer>
      <Header>
        <Title>Recent Documents</Title>
        <ViewAll onClick={handleViewAll}>View All</ViewAll>
      </Header>
      {documents && documents.length > 0 ? (
        <DocumentList>
          {documents.slice(0, 5).map((doc) => (
            <DocumentItem key={doc.id} onClick={() => handleDocumentClick(doc.id)}>
              <DocumentIcon />
              <DocumentName>
                {doc.title}
              </DocumentName>
            </DocumentItem>
          ))}
        </DocumentList>
      ) : (
        <p>No recent documents found.</p>
      )}
    </RecentContainer>
  );
};

export default RecentDocuments;