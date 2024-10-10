// controllers/authController.js

// Import necessary modules
const User = require('../models/userModel'); // Import User model to interact with the database
const jwt = require('jsonwebtoken'); // Import JWT for creating and verifying tokens
const CustomError = require('../utils/customError'); // Custom error handling class
const crypto = require('crypto'); // Import crypto to generate secure tokens
const sendEmail = require('../utils/sendEmail'); // Import a utility function to send emails (e.g., using Nodemailer)

// Helper function to generate JWT for a user
const signToken = (user) => {
    return jwt.sign(
        { id: user._id, role: user.role }, // Payload for JWT
        process.env.JWT_SECRET, // Secret key from .env file
        { expiresIn: process.env.JWT_EXPIRES_IN || '1h' } // Expiry duration
    );
};

// Register a new user
async function register(req, res, next) {
    try {
        const { name, email, password } = req.body;

        // Check if the email is already registered
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return next(new CustomError('Email is already registered', 400));
        }

        // Create a new user and save to the database
        const user = new User({ name, email, password });
        await user.save();

        // Generate a token for the user and respond with the user details
        const token = signToken(user);
        res.status(201).json({ token, user: user.toJSON() });
    } catch (err) {
        console.error('Error during registration:', err);
        next(new CustomError('User registration failed', 400)); // Handle errors with custom message
    }
}

// Login an existing user
async function login(req, res, next) {
    try {
        const { email, password } = req.body;

        // Find the user by email and include the password field
        const user = await User.findOne({ email }).select('+password');
        if (!user || !(await user.comparePassword(password))) {
            return next(new CustomError('Invalid email or password', 401)); // Handle invalid credentials
        }

        // Generate a token and respond with the user details
        const token = signToken(user);
        res.status(200).json({ token, user: user.toJSON() });
    } catch (err) {
        console.error('Error during login:', err);
        next(new CustomError('Login failed', 400)); // Handle errors with custom message
    }
}

// Middleware to protect routes (JWT authentication)
async function protect(req, res, next) {
    try {
        let token;
        // Check if the authorization header contains a Bearer token
        if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
            token = req.headers.authorization.split(' ')[1];
        }

        if (!token) return next(new CustomError('Not authenticated', 401)); // Handle missing token

        // Verify the token and find the user associated with it
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = await User.findById(decoded.id);
        if (!req.user) {
            return next(new CustomError('User no longer exists', 401)); // Handle non-existing user
        }

        // User is authenticated, proceed to the next middleware
        next();
    } catch (err) {
        console.error('Authentication error:', err);
        return next(new CustomError('Not authenticated', 401)); // Handle JWT verification error
    }
}

// Middleware to restrict access to admin-only routes
function restrictToAdmin(req, res, next) {
    if (req.user.role !== 'admin') {
        return next(new CustomError('Access denied: Admin only', 403)); // Handle non-admin access attempt
    }
    next();
}

// Forgot password handler
async function forgotPassword(req, res, next) {
    try {
        const { email } = req.body;
        const user = await User.findOne({ email });
        if (!user) {
            return next(new CustomError('User not found', 404)); // Handle non-existing user
        }

        // Generate a reset token and save it to the user document
        const resetToken = crypto.randomBytes(32).toString('hex');
        user.passwordResetToken = resetToken;
        user.passwordResetExpires = Date.now() + 10 * 60 * 1000; // Set expiration time (10 minutes)
        await user.save();

        // Send the reset token via email (use Nodemailer or any other email service)
        const resetUrl = `${req.protocol}://${req.get('host')}/api/auth/reset-password/${resetToken}`;
        const message = `Forgot your password? Click on this link to reset your password: ${resetUrl}. If you didn't request a password reset, please ignore this email.`;

        await sendEmail({
            email: user.email,
            subject: 'Password Reset Token',
            message,
        });

        res.status(200).json({ message: 'Password reset token sent to email' });
    } catch (err) {
        console.error('Error during password reset:', err);
        next(new CustomError('Password reset failed', 400)); // Handle errors with custom message
    }
}

// Reset password handler
async function resetPassword(req, res, next) {
    try {
        const resetToken = req.params.token;
        const hashedToken = crypto.createHash('sha256').update(resetToken).digest('hex');

        // Find the user by the hashed reset token and check if it's still valid
        const user = await User.findOne({
            passwordResetToken: hashedToken,
            passwordResetExpires: { $gt: Date.now() },
        });

        if (!user) {
            return next(new CustomError('Token is invalid or has expired', 400)); // Handle invalid or expired token
        }

        // Update the password and remove the reset token fields
        user.password = req.body.password;
        user.passwordResetToken = undefined;
        user.passwordResetExpires = undefined;
        await user.save();

        // Generate a new JWT token and respond with the user details
        const token = signToken(user);
        res.status(200).json({ token, user: user.toJSON() });
    } catch (err) {
        console.error('Error during password reset:', err);
        next(new CustomError('Password reset failed', 400)); // Handle errors with custom message
    }
}

// Refresh token handler
async function refreshToken(req, res, next) {
    try {
        const { refreshToken } = req.body;
        if (!refreshToken) {
            return next(new CustomError('No refresh token provided', 400));
        }

        // Verify and decode the refresh token
        const decoded = jwt.verify(refreshToken, process.env.JWT_SECRET);
        const user = await User.findById(decoded.id);
        if (!user) {
            return next(new CustomError('User not found', 404));
        }

        // Create a new JWT token
        const newToken = signToken(user);
        res.status(200).json({ token: newToken });
    } catch (err) {
        console.error('Error during token refresh:', err);
        next(new CustomError('Token refresh failed', 400));
    }
}

// Export all controller functions
module.exports = {
    register,
    login,
    protect,
    restrictToAdmin,
    forgotPassword,
    resetPassword,
    refreshToken,
};
