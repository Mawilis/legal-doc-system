// ~/legal-doc-system/server/utils/catchAsync.js

/**
 * A utility function to catch errors in async functions and pass them to Express error handler.
 * @param {Function} fn - The async function to wrap.
 * @returns {Function} A new function that wraps the original function with a try-catch block.
 */
const catchAsync = (fn) => {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};

module.exports = catchAsync;
