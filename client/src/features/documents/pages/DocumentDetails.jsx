// ~/legal-doc-system/client/src/features/documents/pages/DocumentDetails.jsx

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { markDocumentAsScanned, updateServiceStatus } from '../reducers/documentSlice';
import { io } from 'socket.io-client';
import axios from 'axios';
import styled from 'styled-components';
import { Button, CircularProgress, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';

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
    const { documentId } = useParams();
    const dispatch = useDispatch();
    const [document, setDocument] = useState(null);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState('');
    const [isScannedDialogOpen, setIsScannedDialogOpen] = useState(false);
    const [isServiceStatusDialogOpen, setIsServiceStatusDialogOpen] = useState(false);
    const { loading } = useSelector((state) => state.documents);

    useEffect(() => {
        const socket = io('http://localhost:3001');  // Adjust the URL to match your backend

        const fetchDocument = async () => {
            try {
                const response = await axios.get(`/api/documents/${documentId}`);
                setDocument(response.data);
            } catch (err) {
                console.error('Error fetching document details:', err);
                setError('Error fetching document details. Please try again later.');
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
            setError('Real-time updates are currently unavailable. Please check your connection.');
        });

        return () => {
            socket.disconnect();  // Clean up the socket connection
        };
    }, [documentId]);

    const handleMarkAsScanned = () => {
        setIsScannedDialogOpen(true);
    };

    const confirmMarkAsScanned = () => {
        dispatch(markDocumentAsScanned(documentId));
        setIsScannedDialogOpen(false);
    };

    const handleServiceStatusUpdate = () => {
        setIsServiceStatusDialogOpen(true);
    };

    const confirmServiceStatusUpdate = () => {
        dispatch(updateServiceStatus({ documentId, status: 'Served' }));
        setIsServiceStatusDialogOpen(false);
    };

    if (loading) {
        return (
            <DocumentContainer>
                <CircularProgress />
                <p>Loading document details...</p>
            </DocumentContainer>
        );
    }

    if (error) {
        return <ErrorText>{error}</ErrorText>;
    }

    return (
        <DocumentContainer>
            {document ? (
                <>
                    <Title>{document.title}</Title>
                    <Content>{document.content}</Content>
                    <Button variant="contained" color="primary" onClick={handleMarkAsScanned}>
                        Mark as Scanned
                    </Button>
                    <Button variant="contained" color="secondary" onClick={handleServiceStatusUpdate} style={{ marginLeft: '10px' }}>
                        Update Service Status to Served
                    </Button>
                    {notification && <UpdateNotification>{notification}</UpdateNotification>}

                    {/* Dialog for Marking as Scanned */}
                    <Dialog
                        open={isScannedDialogOpen}
                        onClose={() => setIsScannedDialogOpen(false)}
                    >
                        <DialogTitle>Mark Document as Scanned</DialogTitle>
                        <DialogContent>
                            <DialogContentText>
                                Are you sure you want to mark this document as scanned?
                            </DialogContentText>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setIsScannedDialogOpen(false)} color="secondary">
                                Cancel
                            </Button>
                            <Button onClick={confirmMarkAsScanned} color="primary">
                                Confirm
                            </Button>
                        </DialogActions>
                    </Dialog>

                    {/* Dialog for Service Status Update */}
                    <Dialog
                        open={isServiceStatusDialogOpen}
                        onClose={() => setIsServiceStatusDialogOpen(false)}
                    >
                        <DialogTitle>Update Service Status</DialogTitle>
                        <DialogContent>
                            <DialogContentText>
                                Are you sure you want to update the service status of this document to 'Served'?
                            </DialogContentText>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setIsServiceStatusDialogOpen(false)} color="secondary">
                                Cancel
                            </Button>
                            <Button onClick={confirmServiceStatusUpdate} color="primary">
                                Confirm
                            </Button>
                        </DialogActions>
                    </Dialog>
                </>
            ) : (
                <p>Loading document details...</p>
            )}
        </DocumentContainer>
    );
};

export default DocumentDetails;
