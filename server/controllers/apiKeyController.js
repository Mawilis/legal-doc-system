const ApiKey = require('../models/apiKeyModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');
const crypto = require('crypto');

/**
 * @desc    Get all API keys for the logged-in user
 * @route   GET /api/apikeys
 * @access  Private
 */
exports.getUserApiKeys = async (req, res, next) => {
    try {
        const apiKeys = await ApiKey.find({ user: req.user.id })
            .select('-keyHash')
            .sort('-createdAt');

        res.status(200).json({
            success: true,
            count: apiKeys.length,
            data: apiKeys,
        });
    } catch (error) {
        logger.error(`Error fetching API keys: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Generate a new API key for the logged-in user
 * @route   POST /api/apikeys
 * @access  Private
 */
exports.createApiKey = async (req, res, next) => {
    try {
        const { name, permissions, expiresAt } = req.body;

        if (!name) {
            return next(new CustomError('API key name is required.', 400));
        }

        // Generate a secure API key
        const newKey = `ld_sk_${crypto.randomBytes(24).toString('hex')}`;
        const keyHash = crypto.createHash('sha256').update(newKey).digest('hex');
        const keyPrefix = newKey.substring(0, 8);

        // Save API key metadata
        const apiKey = await ApiKey.create({
            user: req.user.id,
            name,
            keyHash,
            keyPrefix,
            permissions: permissions || ['read_only'],
            expiresAt,
        });

        logger.info(`API key "${apiKey.name}" created for user ${req.user.email}`);

        res.status(201).json({
            success: true,
            message: 'API key generated successfully. Save it securely; it will not be shown again.',
            apiKey: newKey,
        });
    } catch (error) {
        logger.error(`Error creating API key: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Revoke (delete) an API key
 * @route   DELETE /api/apikeys/:id
 * @access  Private
 */
exports.revokeApiKey = async (req, res, next) => {
    try {
        const apiKey = await ApiKey.findById(req.params.id);

        if (!apiKey) {
            return next(new CustomError(`API key not found with id ${req.params.id}`, 404));
        }

        if (apiKey.user.toString() !== req.user.id) {
            return next(new CustomError('User not authorized to revoke this API key.', 403));
        }

        await apiKey.remove();

        logger.info(`API key "${apiKey.name}" revoked by user ${req.user.email}`);

        res.status(200).json({
            success: true,
            data: {},
        });
    } catch (error) {
        logger.error(`Error revoking API key: ${error.message}`);
        next(error);
    }
};
