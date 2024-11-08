const Document = require('../models/documentModel');
const CustomError = require('../utils/customError');

// Create a new document
const createDocument = async (req, res, next) => {
    console.log('Inside createDocument function');
    try {
        const { title, content, client, documentType } = req.body;  // Added more details
        const document = new Document({ title, content, client, documentType, user: req.user.id });
        await document.save();
        res.status(201).json(document);
    } catch (err) {
        console.error('Error in createDocument function:', err);
        next(new CustomError('Failed to create document', 500));
    }
};

// Get a document by ID
const getDocumentById = async (req, res, next) => {
    console.log('Inside getDocumentById function');
    try {
        const document = await Document.findById(req.params.documentId);
        if (!document) return next(new CustomError('Document not found', 404));
        res.status(200).json(document);
    } catch (err) {
        console.error('Error in getDocumentById function:', err);
        next(err);
    }
};

// Get all documents for the authenticated user
const getAllDocuments = async (req, res, next) => {
    console.log('Inside getAllDocuments function');
    try {
        const documents = await Document.find({ user: req.user.id });
        res.status(200).json(documents);
    } catch (err) {
        console.error('Error in getAllDocuments function:', err);
        next(new CustomError('Failed to fetch documents', 500));
    }
};

// Update a document by ID
const updateDocument = async (req, res, next) => {
    console.log('Inside updateDocument function');
    try {
        const document = await Document.findByIdAndUpdate(req.params.documentId, req.body, { new: true });
        if (!document) return next(new CustomError('Document not found', 404));
        res.status(200).json(document);
    } catch (err) {
        console.error('Error in updateDocument function:', err);
        next(err);
    }
};

// Delete a document by ID
const deleteDocument = async (req, res, next) => {
    console.log('Inside deleteDocument function');
    try {
        const document = await Document.findByIdAndDelete(req.params.documentId);
        if (!document) return next(new CustomError('Document not found', 404));
        res.status(200).json({ message: 'Document deleted' });
    } catch (err) {
        console.error('Error in deleteDocument function:', err);
        next(err);
    }
};

// Mark document as scanned
const markDocumentAsScanned = async (req, res, next) => {
    console.log('Inside markDocumentAsScanned function');
    try {
        const document = await Document.findById(req.params.documentId);
        if (!document) return next(new CustomError('Document not found', 404));

        document.scanned = true;
        await document.save();
        res.status(200).json(document);
    } catch (err) {
        console.error('Error in markDocumentAsScanned function:', err);
        next(new CustomError('Failed to mark document as scanned', 500));
    }
};

// Update document service status
const updateServiceStatus = async (req, res, next) => {
    console.log('Inside updateServiceStatus function');
    try {
        const { status } = req.body; // Example statuses: Pending, Served, Failed
        const document = await Document.findById(req.params.documentId);
        if (!document) return next(new CustomError('Document not found', 404));

        document.serviceStatus = status;
        await document.save();
        res.status(200).json(document);
    } catch (err) {
        console.error('Error in updateServiceStatus function:', err);
        next(new CustomError('Failed to update service status', 500));
    }
};

// Export all functions as an object
module.exports = {
    createDocument,
    getDocumentById,
    getAllDocuments,
    updateDocument,
    deleteDocument,
    markDocumentAsScanned,
    updateServiceStatus,
};
