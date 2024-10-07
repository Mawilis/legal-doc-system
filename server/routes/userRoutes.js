const express = require('express');
const userController = require('../controllers/userController');
const authController = require('../controllers/authController');
const router = express.Router();

// Protect all routes after this middleware
router.use(authController.protect);

// Routes for all users
router.get('/me', userController.getProfile);
router.put('/me', userController.updateProfile);

// Admin-only routes
router.use(authController.restrictToAdmin);  // Protect the below routes for admins
router.get('/', userController.getAllUsers);
router.get('/:userId', userController.getUserById);
router.post('/', userController.createUser);
router.put('/:userId', userController.updateUser);
router.delete('/:userId', userController.deleteUser);

module.exports = router;
