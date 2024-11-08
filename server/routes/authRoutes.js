// ~/legal-doc-system/server/routes/authRoutes.js

const express = require('express');
const authController = require('../controllers/authController'); // Controller for authentication routes
const adminController = require('../controllers/adminController'); // Controller for admin routes
const { protect, restrictToAdmin } = require('../controllers/authController'); // Middleware functions

const router = express.Router();

// Public routes for user authentication
router.post('/register', authController.register); // Register a new user
router.post('/login', authController.login); // Login an existing user
router.post('/refresh-token', authController.refreshToken); // Refresh authentication token
router.post('/forgot-password', authController.forgotPassword); // Request a password reset
router.post('/reset-password/:token', authController.resetPassword); // Reset the user's password
router.get('/verify-token', authController.verifyToken); // Verify JWT token

// All routes below this middleware are protected and require the user to be authenticated
router.use(authController.protect); // Apply `protect` middleware

// Admin-only routes (restricted access)
router.get('/users', authController.restrictToAdmin, adminController.getAllUsers); // Get all users
router.post('/users', authController.restrictToAdmin, adminController.createUser); // Create a new user
router.put('/users/:userId', authController.restrictToAdmin, adminController.updateUser); // Update an existing user
router.delete('/users/:userId', authController.restrictToAdmin, adminController.deleteUser); // Delete a user

module.exports = router;
