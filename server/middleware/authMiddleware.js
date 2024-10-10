// middleware/authMiddleware.js

const jwt = require('jsonwebtoken');
const User = require('../models/userModel');  // Import User model
const CustomError = require('../utils/customError');  // Custom error handling

// Middleware to protect routes (JWT authentication)
async function protect(req, res, next) {
    let token;
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        token = req.headers.authorization.split(' ')[1];
    }

    if (!token) {
        return next(new CustomError('Not authenticated', 401));  // Handle missing token
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);  // Verify the token
        req.user = await User.findById(decoded.id);  // Find the user associated with the token
        if (!req.user) {
            return next(new CustomError('User no longer exists', 401));  // Handle non-existing user
        }
        next();
    } catch (err) {
        return next(new CustomError('Not authenticated', 401));  // Handle token verification errors
    }
}

// Middleware to restrict access to admin-only routes
function restrictToAdmin(req, res, next) {
    if (req.user.role !== 'admin') {
        return next(new CustomError('Access denied: Admin only', 403));  // Handle non-admin access attempt
    }
    next();
}

// Export middleware functions
module.exports = {
    protect,
    restrictToAdmin,
};
