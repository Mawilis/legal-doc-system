import express from 'express.js';

const router = express.Router();

router.get('/test', (req, res) => {
  res.json({
    message: 'Test API is working',
    timestamp: new Date().toISOString(),
  });
});

export default router;
