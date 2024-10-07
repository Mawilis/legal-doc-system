import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styled from 'styled-components';

// Styled components for modern UI
const DocumentsContainer = styled.div`
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const DocumentItem = styled.div`
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
`;

const NewDocumentForm = styled.form`
  margin-bottom: 20px;
`;

const Input = styled.input`
  padding: 8px;
  margin-right: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
`;

const Documents = () => {
    const [documents, setDocuments] = useState([]);
    const [newTitle, setNewTitle] = useState('');
    const [error, setError] = useState('');

    // Fetch documents on mount
    useEffect(() => {
        const fetchDocuments = async () => {
            try {
                const response = await axios.get('/api/documents');
                setDocuments(response.data);
                console.log('Documents fetched successfully', response.data);
            } catch (error) {
                console.error('Error fetching documents:', error);
                setError('Failed to fetch documents');
            }
        };

        fetchDocuments();
    }, []);

    const handleCreateDocument = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/api/documents', { title: newTitle });
            setDocuments([...documents, response.data]);
            setNewTitle(''); // Clear input
            console.log('Document created:', response.data);
        } catch (error) {
            console.error('Error creating document:', error);
            setError('Failed to create document');
        }
    };

    const handleDeleteDocument = async (documentId) => {
        try {
            await axios.delete(`/api/documents/${documentId}`);
            setDocuments(documents.filter(doc => doc._id !== documentId));
            console.log(`Document with id ${documentId} deleted`);
        } catch (error) {
            console.error('Error deleting document:', error);
            setError('Failed to delete document');
        }
    };

    return (
        <DocumentsContainer>
            <h1>Documents</h1>
            {error && <p style={{ color: 'red' }}>{error}</p>}

            <NewDocumentForm onSubmit={handleCreateDocument}>
                <Input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="New document title"
                />
                <button type="submit">Create Document</button>
            </NewDocumentForm>

            {documents.map((document) => (
                <DocumentItem key={document._id}>
                    <h3>{document.title}</h3>
                    <button onClick={() => handleDeleteDocument(document._id)}>Delete</button>
                </DocumentItem>
            ))}
        </DocumentsContainer>
    );
};

export default Documents;
