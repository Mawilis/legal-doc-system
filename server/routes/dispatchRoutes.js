const express = require('express');
const router = express.Router();
const { createDispatch, getAllDispatches } = require('../controllers/dispatchController');
const { protect } = require('../middleware/authMiddleware');

router.route('/')
  .post(createDispatch)
  .get(getAllDispatches); // Add protect middleware if auth is fixed

module.exports = router;
