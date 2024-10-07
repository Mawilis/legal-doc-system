const User = require('../models/userModel');
const jwt = require('jsonwebtoken');
const CustomError = require('../utils/customError');
const crypto = require('crypto');

// Helper function to generate JWT
const signToken = (user) => {
    return jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET, {
        expiresIn: process.env.JWT_EXPIRES_IN || '1h',
    });
};

// Register a new user
exports.register = async (req, res, next) => {
    try {
        const { name, email, password } = req.body;

        // Check if the email is already registered
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return next(new CustomError('Email is already registered', 400));
        }

        const user = new User({ name, email, password });
        await user.save();

        const token = signToken(user);
        res.status(201).json({ token, user: user.toJSON() });
    } catch (err) {
        next(new CustomError('User registration failed', 400));
    }
};

// Login an existing user
exports.login = async (req, res, next) => {
    try {
        const { email, password } = req.body;

        // Find the user by email and include the password field
        const user = await User.findOne({ email }).select('+password');
        if (!user || !(await user.comparePassword(password))) {
            return next(new CustomError('Invalid email or password', 401));
        }

        const token = signToken(user);
        res.status(200).json({ token, user: user.toJSON() });
    } catch (err) {
        next(new CustomError('Login failed', 400));
    }
};

// Middleware to protect routes (JWT authentication)
exports.protect = async (req, res, next) => {
    try {
        let token;
        if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
            token = req.headers.authorization.split(' ')[1];
        }

        if (!token) return next(new CustomError('Not authenticated', 401));

        // Verify the token
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = await User.findById(decoded.id);
        if (!req.user) {
            return next(new CustomError('User no longer exists', 401));
        }

        // Proceed to the next middleware
        next();
    } catch (err) {
        return next(new CustomError('Not authenticated', 401));
    }
};

// Middleware to restrict access to admin-only routes
exports.restrictToAdmin = (req, res, next) => {
    if (req.user.role !== 'admin') {
        return next(new CustomError('Access denied: Admin only', 403));
    }
    next();
};

// Forgot password handler (extend functionality as needed)
exports.forgotPassword = async (req, res, next) => {
    try {
        const { email } = req.body;
        const user = await User.findOne({ email });
        if (!user) {
            return next(new CustomError('User not found', 404));
        }

        const resetToken = crypto.randomBytes(32).toString('hex');
        // Save the reset token and expiration (extend logic as required)
        user.passwordResetToken = resetToken;
        user.passwordResetExpires = Date.now() + 10 * 60 * 1000; // 10 minutes
        await user.save();

        // Send email with reset token (implementation depends on the email service used)
        res.status(200).json({ message: 'Password reset token sent to email' });
    } catch (err) {
        next(new CustomError('Password reset failed', 400));
    }
};
