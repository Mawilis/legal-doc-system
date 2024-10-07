// routes/authRoutes.js
const express = require('express');
const authController = require('../controllers/authController');
const adminController = require('../controllers/adminController');
const { protect, restrictToAdmin } = require('../middleware/authMiddleware');  // Import middlewares for role-based access control
const router = express.Router();

// Public routes for authentication
router.post('/register', authController.register);
router.post('/login', authController.login);
router.post('/refresh-token', authController.refreshToken);
router.post('/forgot-password', authController.forgotPassword);
router.post('/reset-password', authController.resetPassword);

// All routes below this line are protected
router.use(protect);

// Protected admin routes
router.get('/users', restrictToAdmin, adminController.getAllUsers);
router.post('/users', restrictToAdmin, adminController.createUser);
router.put('/users/:userId', restrictToAdmin, adminController.updateUser);
router.delete('/users/:userId', restrictToAdmin, adminController.deleteUser);

module.exports = router;
