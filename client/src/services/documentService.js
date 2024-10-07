// client/src/services/documentService.js
import axios from 'axios';

export const getAllDocuments = async () => {
    try {
        const response = await axios.get('/api/documents');
        return response.data;
    } catch (error) {
        console.error('Error fetching documents', error);
        throw error;
    }
};

export const getDocumentById = async (documentId) => {
    try {
        const response = await axios.get(`/api/documents/${documentId}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching document with ID ${documentId}`, error);
        throw error;
    }
};

export const createDocument = async (documentData) => {
    try {
        const response = await axios.post('/api/documents', documentData);
        return response.data;
    } catch (error) {
        console.error('Error creating document', error);
        throw error;
    }
};

export const updateDocument = async (documentId, documentData) => {
    try {
        const response = await axios.put(`/api/documents/${documentId}`, documentData);
        return response.data;
    } catch (error) {
        console.error(`Error updating document with ID ${documentId}`, error);
        throw error;
    }
};

export const deleteDocument = async (documentId) => {
    try {
        const response = await axios.delete(`/api/documents/${documentId}`);
        return response.data;
    } catch (error) {
        console.error(`Error deleting document with ID ${documentId}`, error);
        throw error;
    }
};
