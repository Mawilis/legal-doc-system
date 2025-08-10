import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { io } from 'socket.io-client';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import PageTransition from '../../../components/animations/PageTransition';

// Styled Components
const FormContainer = styled.div`
  padding: 40px;
  max-width: 600px;
  margin: 0 auto;
  background-color: #fdfdfd;
  border-radius: 8px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
`;

const FormTitle = styled.h2`
  text-align: center;
  color: #2c3e50;
  margin-bottom: 24px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  margin-bottom: 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 12px;
  min-height: 140px;
  margin-bottom: 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
`;

const Button = styled.button`
  width: 100%;
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px;
  font-size: 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #0056b3;
  }
`;

const ErrorText = styled.p`
  color: red;
  text-align: center;
  font-weight: 500;
`;

const DocumentForm = () => {
    const { documentId } = useParams();
    const navigate = useNavigate();
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [error, setError] = useState('');
    const socket = io('http://localhost:3001'); // 🔁 Adjust for prod

    useEffect(() => {
        if (documentId) {
            const fetchDoc = async () => {
                try {
                    const res = await axios.get(`/api/documents/${documentId}`);
                    setTitle(res.data.title);
                    setContent(res.data.content);
                } catch (err) {
                    setError('❌ Failed to load the document.');
                }
            };
            fetchDoc();
        }
    }, [documentId]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!title.trim() || !content.trim()) {
            setError('Both title and content are required.');
            return;
        }

        const payload = { title, content };

        try {
            if (documentId) {
                await axios.put(`/api/documents/${documentId}`, payload);
                socket.emit('document-updated', payload);
                toast.success('✅ Document updated');
            } else {
                await axios.post('/api/documents', payload);
                socket.emit('document-created', payload);
                toast.success('✅ Document created');
            }

            navigate('/documents');
        } catch (err) {
            console.error('Submission failed:', err);
            toast.error('🚫 Failed to save document');
        }
    };

    return (
        <PageTransition>
            <FormContainer>
                <FormTitle>{documentId ? 'Edit Document' : 'Create New Document'}</FormTitle>

                {error && <ErrorText>{error}</ErrorText>}

                <form onSubmit={handleSubmit}>
                    <Input
                        type="text"
                        placeholder="Enter Title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                    />
                    <Textarea
                        placeholder="Enter Content"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                    />
                    <Button type="submit">{documentId ? 'Update Document' : 'Create Document'}</Button>
                </form>
            </FormContainer>
        </PageTransition>
    );
};

export default DocumentForm;
