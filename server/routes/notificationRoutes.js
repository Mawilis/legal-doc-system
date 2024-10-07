const express = require('express');
const notificationController = require('../controllers/notificationController');
const authController = require('../controllers/authController');
const router = express.Router();

router.use(authController.protect); // Protect all routes below

router.get('/', notificationController.getAllNotifications);
router.post('/', notificationController.createNotification);
router.patch('/:notificationId', notificationController.markAsRead);
router.delete('/:notificationId', notificationController.deleteNotification);

module.exports = router;
