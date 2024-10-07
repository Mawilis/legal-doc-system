import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { io } from 'socket.io-client';
import axios from 'axios';
import styled from 'styled-components';

// Styled Components for the Document Details UI
const DocumentContainer = styled.div`
  padding: 20px;
  background-color: #f4f4f9;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  margin-bottom: 20px;
  color: #333;
  text-align: center;
`;

const Content = styled.p`
  line-height: 1.6;
  color: #555;
`;

const UpdateNotification = styled.p`
  color: #007bff;
  margin-top: 15px;
  font-style: italic;
`;

const ErrorText = styled.p`
  color: red;
  text-align: center;
`;

const DocumentDetails = () => {
    const { documentId } = useParams();  // Get document ID from route params
    const [document, setDocument] = useState(null);
    const [error, setError] = useState(null); // Error state
    const [notification, setNotification] = useState(''); // Notification for real-time updates
    const socket = io('http://localhost:3001');  // Adjust the URL to match your backend

    useEffect(() => {
        // Fetch the document details from the server
        const fetchDocument = async () => {
            try {
                const response = await axios.get(`/api/documents/${documentId}`);
                setDocument(response.data);
            } catch (err) {
                console.error('Error fetching document details:', err);
                setError('Error fetching document details.');
            }
        };

        fetchDocument();

        // Listen for real-time updates for this document
        socket.on('document-updated', (updatedDocument) => {
            if (updatedDocument._id === documentId) {
                setDocument(updatedDocument);
                setNotification('This document has been updated.');
            }
        });

        // Handle socket connection errors
        socket.on('connect_error', (err) => {
            console.error('Socket connection error:', err);
            setError('Real-time updates are currently unavailable.');
        });

        return () => {
            socket.disconnect();  // Clean up the socket connection
        };
    }, [documentId, socket]);  // Include `socket` in the dependency array

    if (error) {
        return <ErrorText>{error}</ErrorText>;
    }

    return (
        <DocumentContainer>
            {document ? (
                <>
                    <Title>{document.title}</Title>
                    <Content>{document.content}</Content>

                    {notification && <UpdateNotification>{notification}</UpdateNotification>}
                </>
            ) : (
                <p>Loading document details...</p>
            )}
        </DocumentContainer>
    );
};

export default DocumentDetails;
