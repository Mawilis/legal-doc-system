// server/controllers/documentController.js

const Document = require('../models/documentModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Get all documents
 * @route   GET /api/documents
 * @access  Private
 */
exports.getAllDocuments = async (req, res, next) => {
    try {
        // Find all documents and sort them by the most recently created.
        // We use .populate() to automatically replace the 'createdBy' ID with the user's name and email.
        const documents = await Document.find()
            .populate('createdBy', 'name email')
            .sort({ createdAt: -1 });

        res.status(200).json({
            success: true,
            count: documents.length,
            data: documents,
        });
    } catch (error) {
        logger.error(`Error fetching all documents: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get a single document by its ID
 * @route   GET /api/documents/:id
 * @access  Private
 */
exports.getDocumentById = async (req, res, next) => {
    try {
        // Find the document by the ID provided in the URL parameters.
        // We also populate createdBy and assignedTo fields to get user details.
        const document = await Document.findById(req.params.id)
            .populate('createdBy', 'name email')
            .populate('assignedTo', 'name email');

        // If no document is found with that ID, return a 404 error.
        if (!document) {
            return next(new CustomError(`Document not found with id of ${req.params.id}`, 404));
        }

        res.status(200).json({
            success: true,
            data: document,
        });
    } catch (error) {
        logger.error(`Error fetching document by ID: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Create a new document
 * @route   POST /api/documents
 * @access  Private
 */
exports.createDocument = async (req, res, next) => {
    try {
        // Assign the currently logged-in user's ID to the 'createdBy' field.
        // req.user is available thanks to our `protect` middleware.
        req.body.createdBy = req.user.id;

        // The required fields (title, caseNumber, etc.) are taken from the request body.
        const newDocument = await Document.create(req.body);

        logger.info(`New document created: ${newDocument.caseNumber} by ${req.user.email}`);

        res.status(201).json({
            success: true,
            data: newDocument,
        });
    } catch (error) {
        logger.error(`Error creating document: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update a document
 * @route   PUT /api/documents/:id
 * @access  Private
 */
exports.updateDocument = async (req, res, next) => {
    try {
        let document = await Document.findById(req.params.id);

        if (!document) {
            return next(new CustomError(`Document not found with id of ${req.params.id}`, 404));
        }

        // --- Authorization Check ---
        // Ensure that only the user who created the document or an admin can update it.
        // This prevents one user from editing another user's documents.
        if (document.createdBy.toString() !== req.user.id && req.user.role !== 'admin') {
            return next(new CustomError(`User ${req.user.id} is not authorized to update this document.`, 403));
        }

        // Update the document with the new data from the request body.
        // { new: true } returns the modified document.
        // { runValidators: true } ensures that any updates still follow the schema rules (e.g., enums).
        document = await Document.findByIdAndUpdate(req.params.id, req.body, {
            new: true,
            runValidators: true,
        });

        logger.info(`Document updated: ${document.caseNumber}`);

        res.status(200).json({
            success: true,
            data: document,
        });
    } catch (error) {
        logger.error(`Error updating document: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Delete a document
 * @route   DELETE /api/documents/:id
 * @access  Private (Admin Only)
 */
exports.deleteDocument = async (req, res, next) => {
    try {
        const document = await Document.findById(req.params.id);

        if (!document) {
            return next(new CustomError(`Document not found with id of ${req.params.id}`, 404));
        }

        // This is a destructive action, so we already restricted it to admins in the route file.
        // An additional check here provides layered security.
        if (req.user.role !== 'admin') {
            return next(new CustomError(`Only admins can delete documents.`, 403));
        }

        await document.remove();

        logger.info(`Document deleted: ${document.caseNumber}`);

        res.status(200).json({
            success: true,
            data: {}, // No data to return after a successful deletion
        });
    } catch (error) {
        logger.error(`Error deleting document: ${error.message}`);
        next(error);
    }
};


/**
 * @desc    Update a document's status and add a history entry
 * @route   PUT /api/documents/:id/status
 * @access  Private
 */
exports.updateDocumentStatus = async (req, res, next) => {
    try {
        const { status, notes } = req.body;

        // Find the document to update
        const document = await Document.findById(req.params.id);

        if (!document) {
            return next(new CustomError(`Document not found with id of ${req.params.id}`, 404));
        }

        // Update the status
        document.status = status;

        // Add a new entry to the document's history log
        document.history.push({
            action: `Status changed to ${status}`,
            user: req.user.id,
            notes: notes || `Updated by ${req.user.name}`,
        });

        // Save the changes to the database
        await document.save();

        logger.info(`Status updated for document ${document.caseNumber} to ${status}`);

        res.status(200).json({
            success: true,
            data: document,
        });
    } catch (error) {
        logger.error(`Error updating document status: ${error.message}`);
        next(error);
    }
};
