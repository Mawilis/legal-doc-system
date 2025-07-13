// ~/legal-doc-system/client/src/services/apiService.js

// Import necessary libraries
import axios from 'axios';
import { toast } from 'react-toastify';

// Base URL for all API endpoints, retrieved from environment variables
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Create an Axios instance to centralize configurations
const api = axios.create({
    baseURL: API_URL,
    timeout: 10000, // Set request timeout (10 seconds)
});

// Add request interceptor to include auth token in headers
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`; // Include Bearer token if available
        }
        return config;
    },
    (error) => {
        return Promise.reject(error); // Handle request errors
    }
);

// Add response interceptor to handle errors globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        handleError(error); // Call handleError for better error messages
        return Promise.reject(error);
    }
);

// Function to handle different types of API errors
const handleError = (error) => {
    if (error.response) {
        // Server responded with an error
        const { status, data } = error.response;
        switch (status) {
            case 400:
                toast.error(data.message || 'Bad Request. Please check the submitted data.');
                break;
            case 401:
                toast.error('Unauthorized. Please log in again.');
                // Handle auto logout if needed
                localStorage.removeItem('token');
                window.location.href = '/login';
                break;
            case 403:
                toast.error('You do not have permission to perform this action.');
                break;
            case 404:
                toast.error('Resource not found. Please check your request.');
                break;
            case 500:
                toast.error('Server error. Please try again later.');
                break;
            default:
                toast.error(data.message || 'An error occurred while processing your request.');
        }
    } else if (error.request) {
        // No response received from the server
        toast.error('Server did not respond. Please check your network connection and try again.');
    } else {
        // An error occurred in setting up the request
        toast.error('Unexpected error occurred. Please try again.');
    }
};

// Function to get all documents
export const getAllDocuments = async () => {
    try {
        const response = await api.get('/documents');
        return response.data;
    } catch (error) {
        throw error; // Throw error to allow further handling in the calling function
    }
};

// Function to get a document by ID
export const getDocumentById = async (documentId) => {
    try {
        const response = await api.get(`/documents/${documentId}`);
        return response.data;
    } catch (error) {
        throw error; // Throw error to allow further handling in the calling function
    }
};

// Function to create a new document
export const createDocument = async (documentData) => {
    try {
        const response = await api.post('/documents', documentData);
        toast.success('Document created successfully!');
        return response.data;
    } catch (error) {
        throw error; // Throw error to allow further handling in the calling function
    }
};

// Function to update an existing document
export const updateDocument = async (documentId, documentData) => {
    try {
        const response = await api.put(`/documents/${documentId}`, documentData);
        toast.success('Document updated successfully!');
        return response.data;
    } catch (error) {
        throw error; // Throw error to allow further handling in the calling function
    }
};

// Function to delete a document
export const deleteDocument = async (documentId) => {
    try {
        const response = await api.delete(`/documents/${documentId}`);
        toast.success('Document deleted successfully!');
        return response.data;
    } catch (error) {
        throw error; // Throw error to allow further handling in the calling function
    }
};

// Function to get user instructions
export const getInstructions = async () => {
    try {
        const response = await api.get('/instructions');
        return response.data;
    } catch (error) {
        throw error; // Throw error to allow further handling in the calling function
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
