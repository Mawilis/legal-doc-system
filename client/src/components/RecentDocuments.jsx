import React from 'react';
import styled from 'styled-components';
import { FaFileAlt } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const RecentContainer = styled.div`
  background-color: var(--light-color);
  border: 1px solid var(--accent-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-md);
  box-shadow: var(--shadow);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
`;

const Title = styled.h2`
  font-size: 1.5rem;
  color: var(--primary-color);
`;

const ViewAll = styled.button`
  background-color: var(--secondary-color);
  color: var(--light-color);
  border: none;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color var(--transition);

  &:hover {
    background-color: var(--primary-color);
  }
`;

const DocumentList = styled.ul`
  list-style: none;
  padding: 0; // Add padding to reset default ul padding
`;

const DocumentItem = styled.li`
  display: flex;
  align-items: center;
  padding: var(--spacing-xs) 0;
  border-bottom: 1px solid var(--accent-color);

  &:last-child {
    border-bottom: none;
  }
`;

const DocumentIcon = styled(FaFileAlt)`
  color: var(--primary-color);
  margin-right: var(--spacing-xs);
`;

const DocumentName = styled.span`
  font-size: 1rem;
  color: var(--text-color);
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
`;

const RecentDocuments = ({ documents, isLoading }) => { // Add isLoading prop
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
                <div>Loading recent documents...</div>
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
                        <DocumentItem key={doc.id}>
                            <DocumentIcon />
                            <DocumentName onClick={() => handleDocumentClick(doc.id)}>
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