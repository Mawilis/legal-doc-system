// ~/server/middleware/validateObjectId.js

const mongoose = require('mongoose');

/**
 * A middleware that validates if the `id` parameter in the request URL
 * is a valid MongoDB ObjectId.
 *
 * @param {object} req - The Express request object.
 * @param {object} res - The Express response object.
 * @param {Function} next - The next middleware function.
 */
const validateObjectId = (req, res, next) => {
    if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
        // If the ID is not valid, immediately send a 400 Bad Request response.
        return res.status(400).json({
            success: false,
            message: 'Invalid ID format provided.',
        });
    }
    // If the ID is valid, pass control to the next handler.
    next();
};

module.exports = validateObjectId;