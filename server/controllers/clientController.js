// server/controllers/clientController.js

const Client = require('../models/clientModel');
const Document = require('../models/documentModel'); // Import the Document model to perform checks
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

// Note: All functions in this controller are intended for administrative use
// and should be protected by appropriate auth middleware in the routes.

/**
 * @desc    Create a new client
 * @route   POST /api/clients
 * @access  Private/Admin
 */
exports.createClient = async (req, res, next) => {
    try {
        // Securely assign the logged-in user as the manager for this client.
        req.body.managedBy = req.user.id;

        const newClient = await Client.create(req.body);

        logger.info(`New client created: ${newClient.firmName} (Acct: ${newClient.accountNumber})`);

        res.status(201).json({
            success: true,
            data: newClient,
        });
    } catch (error) {
        logger.error(`Error creating client: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get all clients
 * @route   GET /api/clients
 * @access  Private/Admin
 */
exports.getAllClients = async (req, res, next) => {
    try {
        const clients = await Client.find().populate('managedBy', 'name email');

        res.status(200).json({
            success: true,
            count: clients.length,
            data: clients,
        });
    } catch (error) {
        logger.error(`Error fetching all clients: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get a single client by ID
 * @route   GET /api/clients/:id
 * @access  Private/Admin
 */
exports.getClientById = async (req, res, next) => {
    try {
        const client = await Client.findById(req.params.id).populate('managedBy', 'name email');

        if (!client) {
            return next(new CustomError(`Client not found with id of ${req.params.id}`, 404));
        }

        res.status(200).json({
            success: true,
            data: client,
        });
    } catch (error) {
        logger.error(`Error fetching client by ID: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update a client
 * @route   PUT /api/clients/:id
 * @access  Private/Admin
 */
exports.updateClient = async (req, res, next) => {
    try {
        let client = await Client.findById(req.params.id);

        if (!client) {
            return next(new CustomError(`Client not found with id of ${req.params.id}`, 404));
        }

        // Authorization check could be added here if needed, e.g., only the manager or an admin can update.
        // For now, we assume this is an admin-only route.

        client = await Client.findByIdAndUpdate(req.params.id, req.body, {
            new: true,
            runValidators: true,
        });

        logger.info(`Client updated: ${client.firmName}`);

        res.status(200).json({
            success: true,
            data: client,
        });
    } catch (error) {
        logger.error(`Error updating client: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Delete a client
 * @route   DELETE /api/clients/:id
 * @access  Private/Admin
 */
exports.deleteClient = async (req, res, next) => {
    try {
        const client = await Client.findById(req.params.id);

        if (!client) {
            return next(new CustomError(`Client not found with id of ${req.params.id}`, 404));
        }

        // --- Real-world data integrity check ---
        // Check if there are any documents associated with this client that are not in a final state.
        const activeDocuments = await Document.countDocuments({
            client: client.firmName, // Assuming the document model stores the firmName
            status: { $nin: ['Billed', 'Non-Service', 'Cancelled'] } // Statuses that are considered "closed"
        });

        if (activeDocuments > 0) {
            return next(new CustomError(`Cannot delete client. They have ${activeDocuments} active or pending document(s). Please resolve them first.`, 400));
        }

        await client.remove();

        logger.info(`Client deleted: ${client.firmName}`);

        res.status(200).json({
            success: true,
            data: {},
        });
    } catch (error) {
        logger.error(`Error deleting client: ${error.message}`);
        next(error);
    }
};
