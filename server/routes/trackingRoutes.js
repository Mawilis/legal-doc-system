const express = require('express');
const router = express.Router();
const controller = require('../controllers/trackingController');

router.get('/tracking/live', controller.getLiveFleetData);

module.exports = router;
