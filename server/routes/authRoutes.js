const express = require('express');
const authController = require('../controllers/authController');
const adminController = require('../controllers/adminController');
const router = express.Router();

// Public routes
router.post('/register', authController.register);
router.post('/login', authController.login);
router.post('/refresh-token', authController.refreshToken);
router.post('/forgot-password', authController.forgotPassword);
router.post('/reset-password', authController.resetPassword);

// Protected admin routes
router.use(authController.protect); // All routes below will be protected

router.get('/users', authController.restrictToAdmin, adminController.getAllUsers);
router.post('/users', authController.restrictToAdmin, adminController.createUser);
router.put('/users/:userId', authController.restrictToAdmin, adminController.updateUser);
router.delete('/users/:userId', authController.restrictToAdmin, adminController.deleteUser);

module.exports = router;
