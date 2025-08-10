// ~/legal-doc-system/client/src/features/documents/pages/Documents.jsx

import React, { useEffect } from 'react';
import styled from 'styled-components';
import { useDispatch, useSelector } from 'react-redux';
import { fetchDocuments, addDocument, deleteDocument, updateDocument } from '../reducers/documentSlice';
import { FaPlus, FaEdit, FaTrash } from 'react-icons/fa';
import PageTransition from '../../../components/animations/PageTransition';

const DocumentsContainer = styled.div`
  padding: var(--spacing-lg);
  background-color: var(--background-color);
  min-height: 100vh;
`;

const DocumentsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
`;

const DocumentsTitle = styled.h1`
  font-size: 2.5rem;
  color: var(--primary-color);

  @media (max-width: var(--breakpoint-tablet)) {
    font-size: 2rem;
  }

  @media (max-width: var(--breakpoint-mobile)) {
    font-size: 1.75rem;
  }
`;

const AddDocumentButton = styled.button`
  display: flex;
  align-items: center;
  background-color: var(--success-color);
  color: #ffffff;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius);
  transition: background-color var(--transition), transform 0.2s;

  &:hover {
    background-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow);
  }

  &:active {
    transform: translateY(0);
    box-shadow: none;
  }
`;

const DocumentsList = styled.ul`
  list-style: none;
  padding: 0;
`;

const DocumentItem = styled.li`
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  background-color: var(--light-color);
  border: 1px solid var(--accent-color);
  border-radius: var(--border-radius);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: box-shadow var(--transition);

  &:hover {
    box-shadow: var(--shadow);
  }
`;

const DocumentInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const DocumentTitle = styled.h3`
  font-size: 1.25rem;
  color: var(--text-color);
`;

const DocumentDescription = styled.p`
  font-size: 1rem;
  color: var(--secondary-color);
`;

const DocumentActions = styled.div`
  display: flex;
  gap: var(--spacing-xs);
`;

const ErrorMessage = styled.p`
  color: var(--error-color);
`;

const Documents = () => {
  const dispatch = useDispatch();
  const { documents, loading, error } = useSelector((state) => state.documents);

  useEffect(() => {
    dispatch(fetchDocuments());
    document.title = 'Documents | LegalDocSys';
  }, [dispatch]);

  const handleAddDocument = () => {
    const newDoc = {
      title: 'New Document',
      description: 'Description of the new document.',
    };
    dispatch(addDocument(newDoc));
  };

  const handleDeleteDocument = (id) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      dispatch(deleteDocument(id));
    }
  };

  const handleEditDocument = (doc) => {
    const updatedDoc = {
      ...doc,
      title: 'Updated Title',
      description: 'Updated Description',
    };
    dispatch(updateDocument({ id: doc.id, updates: updatedDoc }));
  };

  return (
    <PageTransition>
      <DocumentsContainer>
        <DocumentsHeader>
          <DocumentsTitle>Your Documents</DocumentsTitle>
          <AddDocumentButton onClick={handleAddDocument}>
            <FaPlus style={{ marginRight: '0.5rem' }} /> Add Document
          </AddDocumentButton>
        </DocumentsHeader>

        {loading && <p>Loading documents...</p>}
        {error && <ErrorMessage>{error}</ErrorMessage>}
        {documents?.length === 0 && <p>No documents found.</p>}

        <DocumentsList>
          {documents.map((doc) => (
            <DocumentItem key={doc.id}>
              <DocumentInfo>
                <DocumentTitle>{doc.title}</DocumentTitle>
                <DocumentDescription>{doc.description}</DocumentDescription>
              </DocumentInfo>
              <DocumentActions>
                <button onClick={() => handleEditDocument(doc)}><FaEdit /> Edit</button>
                <button onClick={() => handleDeleteDocument(doc.id)}><FaTrash /> Delete</button>
              </DocumentActions>
            </DocumentItem>
          ))}
        </DocumentsList>
      </DocumentsContainer>
    </PageTransition>
  );
};

export default Documents;
