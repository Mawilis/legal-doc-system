// middleware/authMiddleware.js
const jwt = require('jsonwebtoken');
const User = require('../models/userModel');
const CustomError = require('../utils/customError');  // Custom error class for better error handling

// Middleware to protect routes and check if the user is authenticated
exports.protect = async (req, res, next) => {
    let token;

    // Check for token in headers
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        token = req.headers.authorization.split(' ')[1];
    }

    if (!token) {
        return next(new CustomError('Not authorized, no token provided', 401));
    }

    try {
        // Decode the token to get user ID
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        // Attach user details to the request object (excluding password)
        req.user = await User.findById(decoded.id).select('-password');
        if (!req.user) {
            return next(new CustomError('User not found, token invalid', 404));
        }
        next();
    } catch (error) {
        return next(new CustomError('Not authorized, token failed', 401));
    }
};

// Middleware to check if the user is an admin
exports.admin = (req, res, next) => {
    if (req.user && req.user.role === 'admin') {
        next();
    } else {
        return next(new CustomError('Access denied, admin only', 403));
    }
};

// Middleware to check if the user has a specific role
exports.restrictTo = (...roles) => {
    return (req, res, next) => {
        if (!roles.includes(req.user.role)) {
            return next(new CustomError(`Access denied, this route is restricted to roles: ${roles.join(', ')}`, 403));
        }
        next();
    };
};
