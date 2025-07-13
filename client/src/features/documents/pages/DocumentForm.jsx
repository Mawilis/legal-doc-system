import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { io } from 'socket.io-client';
import styled from 'styled-components';

// Styled Components for the form UI
const FormContainer = styled.div`
  padding: 20px;
  max-width: 600px;
  margin: 20px auto;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const FormTitle = styled.h2`
  text-align: center;
  margin-bottom: 20px;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 5px;
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 5px;
`;

const Button = styled.button`
  width: 100%;
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    background-color: #218838;
  }
`;

const ErrorText = styled.p`
  color: red;
  text-align: center;
`;

const DocumentForm = () => {
    const { documentId } = useParams();  // Get document ID from URL
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const socket = io('http://localhost:3001');  // Adjust to match your backend

    // Fetch document data if editing an existing document
    useEffect(() => {
        if (documentId) {
            const fetchDocument = async () => {
                try {
                    const response = await axios.get(`/api/documents/${documentId}`);
                    setTitle(response.data.title);
                    setContent(response.data.content);
                } catch (err) {
                    console.error('Error fetching document:', err);
                    setError('Failed to load the document');
                }
            };

            fetchDocument();
        }
    }, [documentId]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!title || !content) {
            setError('Both title and content are required');
            return;
        }

        const documentData = { title, content };

        try {
            if (documentId) {
                // Update existing document
                await axios.put(`/api/documents/${documentId}`, documentData);
                socket.emit('document-updated', documentData);  // Notify others about the update
            } else {
                // Create new document
                await axios.post('/api/documents', documentData);
                socket.emit('document-created', documentData);  // Notify others about the new document
            }

            navigate('/documents');  // Redirect after successful submission
        } catch (err) {
            console.error('Error submitting form:', err);
            setError('Failed to save the document');
        }
    };

    return (
        <FormContainer>
            <FormTitle>{documentId ? 'Edit Document' : 'Create New Document'}</FormTitle>

            {error && <ErrorText>{error}</ErrorText>}

            <form onSubmit={handleSubmit}>
                <Input
                    type="text"
                    placeholder="Document Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                />
                <Textarea
                    rows="8"
                    placeholder="Document Content"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                />
                <Button type="submit">{documentId ? 'Update Document' : 'Create Document'}</Button>
            </form>
        </FormContainer>
    );
};

export default DocumentForm;
