'use strict';
const express = require('express');
const router = express.Router();
const controller = require('../controllers/complianceController');
const { protect, admin } = require('../middleware/authMiddleware');

// Safety Wrapper
const safe = (fn) => fn ? fn : (req, res) => res.status(501).json({msg: 'Not Implemented'});

// Auth Special Case
if ('compliance' === 'auth') {
    router.post('/register', safe(controller.register));
    router.post('/login', safe(controller.login));
    router.get('/logout', safe(controller.logout));
    router.get('/me', protect, safe(controller.getMe));
} 
// Dashboard Special Case
else if ('compliance' === 'dashboard') {
    router.get('/', protect, safe(controller.getAll));
} 
// Standard CRUD
else {
    router.route('/').get(protect, safe(controller.getAll)).post(protect, safe(controller.create));
    router.route('/:id').get(protect, safe(controller.getOne)).put(protect, safe(controller.update)).delete(protect, admin, safe(controller.remove));
}

module.exports = router;
