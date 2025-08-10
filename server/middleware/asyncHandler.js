// ~/server/middleware/asyncHandler.js

/**
 * A middleware utility that wraps asynchronous route handlers to catch errors.
 * This prevents the need for repetitive try/catch blocks in every controller.
 *
 * @param {Function} fn - The asynchronous controller function to execute.
 * @returns {Function} An Express middleware function that executes the controller and catches errors.
 */
const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
};

module.exports = asyncHandler;