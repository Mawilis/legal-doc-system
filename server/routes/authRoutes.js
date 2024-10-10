// routes/authRoutes.js

const express = require('express');
const authController = require('../controllers/authController'); // Controller for authentication routes
const adminController = require('../controllers/adminController'); // Controller for admin routes
const { protect, restrictToAdmin } = require('../middleware/authMiddleware'); // Middleware for authentication and role-based access control

const router = express.Router();

// Debug log to ensure the `authController` is correctly imported and defined
console.log('Auth Controller Functions:', Object.keys(authController));

// Check if each function in `authController` exists and is a function
for (const [key, value] of Object.entries(authController)) {
    console.log(`Function ${key} defined:`, typeof value === 'function');
}

// Check for undefined controller functions and log error messages
if (typeof authController.register !== 'function') {
    console.error('Error: `authController.register` is not defined or not a function.');
}
if (typeof authController.login !== 'function') {
    console.error('Error: `authController.login` is not defined or not a function.');
}
if (typeof authController.forgotPassword !== 'function') {
    console.error('Error: `authController.forgotPassword` is not defined or not a function.');
}
if (typeof authController.resetPassword !== 'function') {
    console.error('Error: `authController.resetPassword` is not defined or not a function.');
}
if (typeof authController.refreshToken !== 'function') {
    console.error('Error: `authController.refreshToken` is not defined or not a function.');
}

// Public routes for user authentication
router.post('/register', authController.register); // Register a new user
router.post('/login', authController.login); // Login an existing user
router.post('/refresh-token', authController.refreshToken); // Refresh authentication token
router.post('/forgot-password', authController.forgotPassword); // Request a password reset
router.post('/reset-password/:token', authController.resetPassword); // Reset the user's password

// All routes below this middleware are protected and require the user to be authenticated
router.use(protect);  // Apply `protect` middleware to secure these routes

// Admin-only routes (restricted access)
router.get('/users', restrictToAdmin, adminController.getAllUsers); // Get all users
router.post('/users', restrictToAdmin, adminController.createUser); // Create a new user
router.put('/users/:userId', restrictToAdmin, adminController.updateUser); // Update an existing user
router.delete('/users/:userId', restrictToAdmin, adminController.deleteUser); // Delete a user

// Debug log to confirm that the router was created successfully
console.log('Auth routes set up successfully.');

module.exports = router;
