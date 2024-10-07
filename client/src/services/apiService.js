import axios from 'axios';
import { toast } from 'react-toastify';

const API_URL = '/api'; // Base URL for all API endpoints

// Get all documents
export const getAllDocuments = async () => {
    try {
        const response = await axios.get(`${API_URL}/documents`);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Get document by ID
export const getDocumentById = async (documentId) => {
    try {
        const response = await axios.get(`${API_URL}/documents/${documentId}`);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Create a new document
export const createDocument = async (documentData) => {
    try {
        const response = await axios.post(`${API_URL}/documents`, documentData);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Update an existing document
export const updateDocument = async (documentId, documentData) => {
    try {
        const response = await axios.put(`${API_URL}/documents/${documentId}`, documentData);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Delete a document
export const deleteDocument = async (documentId) => {
    try {
        const response = await axios.delete(`${API_URL}/documents/${documentId}`);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Fetch user instructions
export const getInstructions = async () => {
    try {
        const response = await axios.get(`${API_URL}/instructions`);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Handle errors and display notifications
const handleError = (error) => {
    if (error.response) {
        // Server responded with an error
        toast.error(error.response.data.message || 'An error occurred while processing your request.');
    } else if (error.request) {
        // No response received from the server
        toast.error('Server did not respond. Please try again later.');
    } else {
        // An error occurred in setting up the request
        toast.error('Unexpected error occurred. Please try again.');
    }
};

// Export the services
const apiService = {
    getAllDocuments,
    getDocumentById,
    createDocument,
    updateDocument,
    deleteDocument,
    getInstructions,
};

export default apiService;
