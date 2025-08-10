// ~/client/src/features/documents/pages/DocumentDetails.jsx

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { markDocumentAsScanned, updateServiceStatus } from '../reducers/documentSlice';
import { io } from 'socket.io-client';
import axios from 'axios';
import styled from 'styled-components';
import {
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle
} from '@mui/material';
import PageTransition from '../../../components/animations/PageTransition';

// Styled Components
const DocumentContainer = styled.div`
  padding: 40px;
  background-color: #f4f4f9;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  margin-bottom: 20px;
  color: #2c3e50;
  text-align: center;
`;

const Content = styled.p`
  line-height: 1.6;
  color: #555;
  white-space: pre-wrap;
`;

const UpdateNotification = styled.p`
  color: #007bff;
  margin-top: 15px;
  font-style: italic;
`;

const ErrorText = styled.p`
  color: red;
  text-align: center;
  font-weight: 500;
`;

const Actions = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
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
        const socket = io('http://localhost:3001'); // Replace with your backend URL

        const fetchDocument = async () => {
            try {
                const response = await axios.get(`/api/documents/${documentId}`);
                setDocument(response.data);
            } catch (err) {
                console.error('Error fetching document:', err);
                setError('Unable to fetch document. Please try again later.');
            }
        };

        fetchDocument();

        socket.on('document-updated', (updatedDocument) => {
            if (updatedDocument._id === documentId) {
                setDocument(updatedDocument);
                setNotification('🔄 This document was updated in real-time.');
            }
        });

        socket.on('connect_error', () => {
            setError('Real-time connection failed. Offline updates only.');
        });

        return () => socket.disconnect();
    }, [documentId]);

    const handleMarkAsScanned = () => setIsScannedDialogOpen(true);
    const confirmMarkAsScanned = () => {
        dispatch(markDocumentAsScanned(documentId));
        setIsScannedDialogOpen(false);
    };

    const handleServiceStatusUpdate = () => setIsServiceStatusDialogOpen(true);
    const confirmServiceStatusUpdate = () => {
        dispatch(updateServiceStatus({ documentId, status: 'Served' }));
        setIsServiceStatusDialogOpen(false);
    };

    if (loading) {
        return (
            <DocumentContainer>
                <CircularProgress />
                <p>Loading document...</p>
            </DocumentContainer>
        );
    }

    if (error) {
        return (
            <DocumentContainer>
                <ErrorText>{error}</ErrorText>
            </DocumentContainer>
        );
    }

    return (
        <PageTransition>
            <DocumentContainer>
                {document ? (
                    <>
                        <Title>{document.title}</Title>
                        <Content>{document.content}</Content>

                        <Actions>
                            <Button variant="contained" color="primary" onClick={handleMarkAsScanned}>
                                Mark as Scanned
                            </Button>
                            <Button
                                variant="contained"
                                color="secondary"
                                onClick={handleServiceStatusUpdate}
                            >
                                Update to Served
                            </Button>
                        </Actions>

                        {notification && <UpdateNotification>{notification}</UpdateNotification>}

                        {/* Scan Confirmation Dialog */}
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
                                <Button onClick={() => setIsScannedDialogOpen(false)} color="inherit">
                                    Cancel
                                </Button>
                                <Button onClick={confirmMarkAsScanned} color="primary">
                                    Confirm
                                </Button>
                            </DialogActions>
                        </Dialog>

                        {/* Service Status Update Dialog */}
                        <Dialog
                            open={isServiceStatusDialogOpen}
                            onClose={() => setIsServiceStatusDialogOpen(false)}
                        >
                            <DialogTitle>Update Service Status</DialogTitle>
                            <DialogContent>
                                <DialogContentText>
                                    Update this document's service status to <strong>"Served"</strong>?
                                </DialogContentText>
                            </DialogContent>
                            <DialogActions>
                                <Button onClick={() => setIsServiceStatusDialogOpen(false)} color="inherit">
                                    Cancel
                                </Button>
                                <Button onClick={confirmServiceStatusUpdate} color="secondary">
                                    Confirm
                                </Button>
                            </DialogActions>
                        </Dialog>
                    </>
                ) : (
                    <p>No document found.</p>
                )}
            </DocumentContainer>
        </PageTransition>
    );
};

export default DocumentDetails;
