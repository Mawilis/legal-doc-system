// ~/legal-doc-system/server/routes/authRoutes.js

const express = require('express');
const authController = require('../controllers/authController');
const router = express.Router();

// Register route
router.post('/register', authController.register);

// Login route
router.post('/login', authController.login);

// Forgot password route
router.post('/forgot-password', authController.forgotPassword);

// Reset password route
router.patch('/reset-password/:token', authController.resetPassword);

// Refresh token route
router.post('/refresh-token', authController.refreshToken);

// Protect routes (e.g., for updating user details, deleting accounts, etc.)
router.use(authController.protect);

// Example of a restricted admin route
router.use(authController.restrictToAdmin);

module.exports = router;
